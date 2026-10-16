#!/usr/bin/env bash
set -e

echo "Starting FlowSync-AI on Render..."
PORT="${PORT:-8501}"
exec streamlit run FlowSync-AI/app.py \
    --server.port "$PORT" \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.enableCORS false \
    --server.enableXsrfProtection false
