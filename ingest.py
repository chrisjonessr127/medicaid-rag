"""Validate demo files and atomically refresh the active RAG records."""
from pathlib import Path

from rag_core import client, connect, setting, vector_literal

ROOT = Path(__file__).resolve().parent
DOC_DIR = ROOT / "data"
BANNER = "FICTIONAL DEMO DATA — NOT REAL POLICY"


def main():
    files = sorted(DOC_DIR.glob("demo_*.txt"))
    if not files:
        raise SystemExit("No demo documents. Run python generate_demo_data.py first.")

    chunks = []
    for file in files:
        text = file.read_text(encoding="utf-8")
        if not text.startswith(BANNER):
            raise SystemExit(f"Refusing non-demo document: {file.name}")
        for paragraph in text.split("\n\n")[1:]:
            paragraph = paragraph.strip()
            if len(paragraph) > 30:
                chunks.append((file.name, paragraph))
    if not chunks:
        raise SystemExit("No usable demonstration paragraphs.")

    # Generate and validate EVERY embedding before altering active rows.
    vectors = []
    ai = client()
    for start in range(0, len(chunks), 12):
        batch = chunks[start:start + 12]
        result = ai.embed(
            model=setting("EMBEDDING_MODEL", "nomic-embed-text"),
            input=["search_document: " + content for _, content in batch],
        )
        if len(result.embeddings) != len(batch):
            raise RuntimeError("Embedding service returned the wrong number of vectors")
        vectors.extend(vector_literal(item) for item in result.embeddings)

    with connect() as connection:
        connection.execute("CREATE EXTENSION IF NOT EXISTS vector")
        connection.execute("""
            CREATE TABLE IF NOT EXISTS rag_documents (
                id bigserial PRIMARY KEY,
                filename text NOT NULL,
                content text NOT NULL,
                embedding vector(768) NOT NULL,
                indexed_at timestamptz NOT NULL DEFAULT now()
            )
        """)
        with connection.transaction():
            connection.execute("DELETE FROM rag_documents")
            with connection.cursor() as cursor:
                cursor.executemany(
                    "INSERT INTO rag_documents (filename, content, embedding) "
                    "VALUES (%s, %s, %s::vector)",
                    [(source, content, vector) for (source, content), vector
                     in zip(chunks, vectors)],
                )
    print(f"Indexed {len(chunks)} fictional passages from {len(files)} files.")


if __name__ == "__main__":
    main()
