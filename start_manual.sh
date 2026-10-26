#!/bin/bash
cd /home/caj12/medicaid-rag

# 1. Dynamically route connection to Windows Ollama engine
export OLLAMA_HOST="http://$(ip route show | grep -i default | awk '{ print $3 }'):11434"

# 2. Start PostgreSQL container
echo "[1/3] Starting database container..."
sudo podman-compose up -d

# 3. Clean up any stale instances
pkill -f streamlit
pkill -f cloudflared

# 4. Start Streamlit web server in the background
echo "[2/3] Starting Streamlit..."
source venv/bin/activate
nohup streamlit run chat_ui.py > streamlit.log 2>&1 &
sleep 3

# 5. Launch Cloudflare Quick Tunnel in the foreground to display the URL
echo "[3/3] Launching Cloudflare Tunnel..."
echo ""
echo "=================================================================="
echo " Copy the https://....trycloudflare.com link below when it appears."
echo " Keep this window OPEN while using the assistant."
echo " Close this window or run Stop_Assistant.bat when finished."
echo "=================================================================="
echo ""

cloudflared tunnel --url http://localhost:8501
