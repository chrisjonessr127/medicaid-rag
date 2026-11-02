# Local RAG Assistant

A self-hosted Retrieval-Augmented Generation research prototype.

## Technology
- Ollama local inference
- PostgreSQL with pgvector
- Streamlit chat interface
- Python document ingestion
- Semantic search with source references

## Data
No employer documents or proprietary datasets are distributed.
Create a local data directory and add authorized test documents.

## Security
This is a development prototype, not a production-certified system.
Review database credentials, network access and external synchronization
before use with sensitive documents.

## Local startup
Run podman-compose up -d.
Create a Python virtual environment and install the dependencies.
Pull the Ollama models llama3.2 and nomic-embed-text.
Ingest your local demo documents using python ingest.py.
Start the interface using:
streamlit run chat_ui.py --server.address 127.0.0.1
