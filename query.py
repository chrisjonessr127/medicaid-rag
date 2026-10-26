import sys
import ollama
import psycopg
from pgvector.psycopg import register_vector

if len(sys.argv) < 2:
    print("Usage: python query.py '<Your question here>'")
    sys.exit(1)

query = sys.argv[1]

conn = psycopg.connect("dbname=medicaid user=admin password=password host=127.0.0.1", autocommit=True)
register_vector(conn)

# Embed query with Nomic search prefix
query_embedding = ollama.embed(model='nomic-embed-text', input=f"search_query: {query}").embeddings[0]

# Cosine similarity retrieval
result = conn.execute(
    'SELECT filename, content FROM comar_rules ORDER BY embedding <=> %s::vector LIMIT 5', 
    (query_embedding,)
).fetchall()

if not result:
    print("No relevant context found in database.")
    sys.exit(0)

context = ""
for row in result:
    context += f"--- Source File: {row[0]} ---\n{row[1]}\n\n"

prompt = f"""You are a Maryland Medicaid and Long-Term Care administrative expert. 
Answer the user's question accurately using ONLY the provided regulatory and operational context. 
Cite the source file and any specific rules, limits, or guidelines mentioned. 
If the answer cannot be determined from the context, state: 'The provided documentation does not contain this information.'

Context:
{context}

Question: {query}
"""

print(f"Retrieving context and prompting Llama 3.2...\n")
response = ollama.generate(model='llama3.2', prompt=prompt)

print("=== EXPERT RESPONSE ===")
print(response.response)
