#!/usr/bin/env bash
# startOllama.sh - install Ollama and fetch the lab model. Runs once, at
# postCreate. It does NOT start the long-lived server and it does NOT warm the
# model: the container is rebuilt/restarted after this, so anything loaded into
# RAM here would be thrown away. serveOllama.sh (postStart) does that part.
set -euo pipefail

MODEL="llama3.2"   # must match MODEL in lab1/agent_helpers.py

echo "== Ollama setup =="

if ! command -v ollama >/dev/null 2>&1; then
  echo "Installing Ollama..."
  if ! command -v zstd >/dev/null 2>&1 && command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y && sudo apt-get install -y zstd curl ca-certificates
  fi
  curl -fsSL https://ollama.com/install.sh | sh
fi
echo "OK: ollama present"

# A server has to be up to pull. Start a throwaway one just for the download.
ollama serve >/tmp/ollama-pull.log 2>&1 &
PULL_PID=$!
trap 'kill "$PULL_PID" 2>/dev/null || true' EXIT

for _ in $(seq 1 30); do
  curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && break
  sleep 1
done

if ollama list 2>/dev/null | grep -q "^${MODEL}"; then
  echo "OK: ${MODEL} already present"
else
  echo "Pulling ${MODEL} (a few minutes, once)..."
  ollama pull "${MODEL}"
fi

ollama list || true
echo "OK: model ready. serveOllama.sh will start and warm it on container start."
