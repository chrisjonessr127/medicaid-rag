import os
import ollama
import psycopg
from pgvector.psycopg import register_vector
from datetime import datetime

DATA_DIR = "data"
generation_id = datetime.now().strftime("%Y%m%d_%H%M%S")

print("Connecting to PostgreSQL at 127.0.0.1:5432...")
# autocommit=True is disabled so we can manually manage transactions
conn = psycopg.connect("dbname=medicaid user=admin password=password host=127.0.0.1")
conn.execute('CREATE EXTENSION IF NOT EXISTS vector')
register_vector(conn)

print("Creating staging table...")
conn.execute('''
    CREATE TABLE comar_rules_staging (
        id bigserial PRIMARY KEY, 
        filename text, 
        content text, 
        embedding vector(768),
        generation_id text
    )
''')
conn.commit()

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

print(f"Generating embeddings for {len(chunks)} chunks...")
inputs = ["search_document: " + chunk[1] for chunk in chunks]
embeddings_response = ollama.embed(model='nomic-embed-text', input=inputs)

print("Writing vectors into staging table...")
cur = conn.cursor()
with cur.copy("COPY comar_rules_staging (filename, content, embedding, generation_id) FROM STDIN WITH (FORMAT BINARY)") as copy:
    copy.set_types(['text', 'text', 'vector', 'text'])
    for (filename, content), embedding in zip(chunks, embeddings_response.embeddings):
        copy.write_row([filename, content, embedding, generation_id])
conn.commit()

print("Executing zero-downtime table swap...")
# Defensive SQL swap ensuring active index is never dropped mid-generation
with conn.transaction():
    conn.execute("DROP TABLE IF EXISTS comar_rules_backup")
    conn.execute("ALTER TABLE IF EXISTS comar_rules RENAME TO comar_rules_backup")
    conn.execute("ALTER TABLE comar_rules_staging RENAME TO comar_rules")

print(f"Ingestion successful! Generation {generation_id} is now active.")
