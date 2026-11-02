#!/usr/bin/env bash
set -euo pipefail

cd -- "$(dirname -- "${BASH_SOURCE[0]}")"

sudo podman-compose up -d

source venv/bin/activate

streamlit run chat_ui.py --server.address 127.0.0.1
