# Local RAG — Fully Fictional Demonstration

Local, CPU-capable RAG prototype built with Ollama, PostgreSQL/pgvector and Streamlit.
The repository contains **no employer or facility documents** on its current branch.
All new demonstration data is generated locally, labeled fictional and ignored by Git.
This is not health, legal, insurance, government, or eligibility advice.

## Ubuntu WSL quick start (run inside repository root)

1. Install Docker Desktop with WSL integration **or** Podman Compose. Start the engine.
2. Create the Python environment and install dependencies:

   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt

3. Run `python generate_demo_data.py` to create 8 fake policy documents.
4. Run `docker compose up -d` (or `podman-compose up -d`). The Postgres image is downloaded once.
5. Ensure Ollama is running on the localhost URL recorded in `.env`. Pull models:

   ollama pull nomic-embed-text
   ollama pull llama3.2

6. Run `python ingest.py` then `python query.py 'When is a demo application acknowledged?'`.
7. Start the UI: `streamlit run chat_ui.py --server.address 127.0.0.1`.
   Open http://localhost:8501 on the same machine.
8. Unit checks: `python -m unittest discover -s tests -v`.

### Windows-host Ollama with WSL2

If Ollama is running on Windows rather than Ubuntu, update `OLLAMA_HOST` in your
ignored `.env` to a Windows-host URL **that you have verified works from WSL2**.
Depending on WSL networking mode, localhost or the Windows host gateway may work.
Do not publish the Ollama API to the public Internet.

## Operational safety

- New isolated database volume: `medicaid_rag_synthetic_demo_pgdata`; **old database volume is untouched**.
- Database listens on `127.0.0.1:55432` only; credentials are randomized in ignored `.env`.
- The demo ingestion only reads `data/demo_*.txt` with a mandatory fictional banner.
- Every new embedding is generated **before** an atomic delete/replace transaction.
- No public tunnel or external-site synchronization is enabled by the startup scripts.
- Model downloads require Internet; inference uses the configured Ollama endpoint.
- Generated data is not committed, and tests are included. This is still a developer demo, not a production/compliance-certified system.
- Any previously published employer documents may remain in **older Git history**. Editing files on `main` does not purge that history or copies downloaded by others.
