# Local GPU-Accelerated RAG Assistant (LTC & Medicaid)

An enterprise-grade, fully local Retrieval-Augmented Generation (RAG) pipeline designed to navigate complex Long-Term Care (LTC) and Maryland Medicaid regulations. 

Designed for healthcare administrative offices, this system ensures 100% data privacy by executing all vector embeddings and Large Language Model (LLM) inference on local hardware, completely air-gapped from commercial APIs.

## 🚀 Architecture & Tech Stack
- **Frontend:** Streamlit (Python) with custom session-state memory for a conversational UI.
- **Database:** Containerized PostgreSQL with the `pgvector` extension (deployed via Podman).
- **AI Inference Engine:** Ollama (Llama 3.2 3B & Nomic-Embed-Text).
- **Hardware Acceleration:** Deployed in a hybrid Windows/WSL2 environment, utilizing cross-subsystem networking to route Linux container traffic directly to the Windows host's AMD GPU via the Vulkan API.
- **Remote Access:** Cloudflared (Cloudflare Tunnels) for secure, zero-trust mobile access without opening router ports.

## 💡 Key Features
- **Automated Ingestion:** Python script chunks and embeds raw regulatory text files into the vector database.
- **Transparent Sourcing:** The UI includes an expandable source-tracking module, allowing users to verify the exact document and paragraph the AI used to generate its answer.
- **Contextual Memory:** Maintains chat history within the browser session for natural follow-up questions.
- **Background Automation:** Managed via custom bash and batch scripting for silent, on-demand execution.

## 🛡️ Security & Privacy
Healthcare data requires strict compliance. By utilizing local models and a Podman-isolated database, zero Protected Health Information (PHI) or proprietary operational data ever leaves the host machine.
