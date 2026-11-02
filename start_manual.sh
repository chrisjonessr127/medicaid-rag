#!/usr/bin/env bash
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
[[ -f .env ]] || { echo 'Missing .env. Run the repair script.' >&2; exit 1; }
if docker compose version >/dev/null 2>&1; then
  docker compose up -d
elif command -v podman-compose >/dev/null 2>&1; then
  podman-compose up -d
else
  echo 'Install Docker Compose or podman-compose.' >&2
  exit 1
fi
if [[ -f .venv/bin/activate ]]; then
  source .venv/bin/activate
elif [[ -f venv/bin/activate ]]; then
  source venv/bin/activate
else
  echo 'Create a virtual environment and install requirements.txt.' >&2
  exit 1
fi
exec streamlit run chat_ui.py --server.address 127.0.0.1
