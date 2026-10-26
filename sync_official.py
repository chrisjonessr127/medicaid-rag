import requests
from bs4 import BeautifulSoup
import hashlib
import ollama
import psycopg
from pgvector.psycopg import register_vector

# Add the specific Maryland Medicaid URLs you want to monitor here
TARGET_URLS = [
    "https://health.maryland.gov/mmcp/Pages/Provider-Information.aspx",
    # You can add direct COMAR e-regulation links or MDH manual links here
]

print("Connecting to PostgreSQL...")
conn = psycopg.connect("dbname=medicaid user=admin password=password host=127.0.0.1", autocommit=True)
register_vector(conn)

# Create a table to track website changes
conn.execute('''
    CREATE TABLE IF NOT EXISTS document_hashes (
        url text PRIMARY KEY,
        md5_hash text,
        last_updated timestamp DEFAULT CURRENT_TIMESTAMP
    )
''')

for url in TARGET_URLS:
    print(f"Checking {url} for updates...")
    try:
        # Use a standard browser user-agent to bypass basic firewall blocks
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract the raw text from the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        text_content = ' '.join(soup.stripped_strings)
        
        if len(text_content) < 100:
            print("Content too short, skipping.")
            continue

        # Generate a fingerprint of the current live website
        current_hash = hashlib.md5(text_content.encode('utf-8')).hexdigest()
        
        cur = conn.cursor()
        cur.execute("SELECT md5_hash FROM document_hashes WHERE url = %s", (url,))
        result = cur.fetchone()
        
        if result and result[0] == current_hash:
            print(f"No regulatory changes detected for {url}. Skipping.")
            continue
            
        print("Changes detected! Updating database...")
        
        # Step 1: Delete the outdated rules for this specific URL
        cur.execute("DELETE FROM comar_rules WHERE filename = %s", (url,))
        
        # Step 2: Chunk the new text by periods (sentences) to fit into the embedding model
        paragraphs = [p.strip() for p in text_content.split('. ') if len(p.strip()) > 40]
        
        # Step 3: Embed the new chunks
        inputs = ["search_document: " + p for p in paragraphs]
        embeddings_response = ollama.embed(model='nomic-embed-text', input=inputs)
        
        # Step 4: Save the new vectors
        with cur.copy("COPY comar_rules (filename, content, embedding) FROM STDIN WITH (FORMAT BINARY)") as copy:
            copy.set_types(['text', 'text', 'vector'])
            for content, embedding in zip(paragraphs, embeddings_response.embeddings):
                copy.write_row([url, content, embedding])
        
        # Step 5: Save the new fingerprint so we don't update it again until it changes
        cur.execute('''
            INSERT INTO document_hashes (url, md5_hash, last_updated) 
            VALUES (%s, %s, CURRENT_TIMESTAMP) 
            ON CONFLICT (url) DO UPDATE SET md5_hash = EXCLUDED.md5_hash, last_updated = CURRENT_TIMESTAMP
        ''', (url, current_hash))
        
        print(f"Successfully updated database with the latest rules from {url}")
        
    except Exception as e:
        print(f"Failed to process {url}: {e}")

print("Sync complete!")
