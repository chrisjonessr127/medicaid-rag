import os
import ollama
import psycopg
from pgvector.psycopg import register_vector

DATA_DIR = "data"

print("Connecting to PostgreSQL at 127.0.0.1:5432...")
conn = psycopg.connect("dbname=medicaid user=admin password=password host=127.0.0.1", autocommit=True)
conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
register_vector(conn)

# Recreate the table to accept fresh vectors
conn.execute('DROP TABLE IF EXISTS comar_rules')
conn.execute('''
    CREATE TABLE comar_rules (
        id bigserial PRIMARY KEY, 
        filename text, 
        content text, 
        embedding vector(768)
    )
''')

chunks = []
print(f"Parsing documents from '{DATA_DIR}/'...")
for filename in sorted(os.listdir(DATA_DIR)):
    if filename.endswith(".txt"):
        filepath = os.path.join(DATA_DIR, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
            paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 30]
            for p in paragraphs:
                chunks.append((filename, p))

if not chunks:
    print("Error: No text files found in the data/ folder.")
    exit(1)

print(f"Generating embeddings for {len(chunks)} chunks via nomic-embed-text...")
inputs = ["search_document: " + chunk[1] for chunk in chunks]
embeddings_response = ollama.embed(model='nomic-embed-text', input=inputs)

print("Writing vectors into PostgreSQL...")
cur = conn.cursor()
with cur.copy("COPY comar_rules (filename, content, embedding) FROM STDIN WITH (FORMAT BINARY)") as copy:
    copy.set_types(['text', 'text', 'vector'])
    for (filename, content), embedding in zip(chunks, embeddings_response.embeddings):
        copy.write_row([filename, content, embedding])

print(f"Ingestion successful! Loaded {len(chunks)} chunks into the database.")
