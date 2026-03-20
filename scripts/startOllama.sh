
#!/bin/bash
# startup_ollama.sh - Start and warm up Ollama for lab exercises

#!/usr/bin/env bash
set -euo pipefail

# ---- Ensure prerequisites ----
install_zstd() {
  if command -v zstd >/dev/null 2>&1; then
    echo "zstd already installed"
    return
  fi

  echo "Installing zstd..."

  if command -v apt-get >/dev/null 2>&1; then
    sudo apt-get update -y
    sudo apt-get install -y zstd curl ca-certificates
  elif command -v dnf >/dev/null 2>&1; then
    sudo dnf install -y zstd curl ca-certificates
  elif command -v yum >/dev/null 2>&1; then
    sudo yum install -y zstd curl ca-certificates
  elif command -v pacman >/dev/null 2>&1; then
    sudo pacman -Sy --noconfirm zstd curl ca-certificates
  else
    echo "ERROR: Unsupported package manager. Install 'zstd' manually and rerun."
    exit 1
  fi
}

echo "========================================"
echo "Ollama Startup & Warmup Script"
echo "========================================"
echo ""

# Step 1: Check and install Ollama if needed
echo "Step 1: Checking for Ollama installation..."
if command -v ollama &> /dev/null; then
    echo "✓ Ollama is already installed"
else
    echo "  Installing Ollama..."
    install_zstd
    curl -fsSL https://ollama.com/install.sh | sh
    echo "✓ Ollama installed"
fi
echo ""

# Step 2: Start Ollama service
echo "Step 2: Starting Ollama service..."
ollama serve > /dev/null 2>&1 &
OLLAMA_PID=$!
echo "✓ Ollama started (PID: $OLLAMA_PID)"
echo ""

# Wait for Ollama to be ready
echo "Step 3: Waiting for Ollama to be ready..."
sleep 3
until curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    echo "  Waiting for Ollama server..."
    sleep 1
done
echo "✓ Ollama server is ready"
echo ""

# Step 4: Pull llama3.2:3b model if not present
echo "Step 4: Checking for llama3.2:3b model..."
if ollama list | grep -q "llama3.2:3b"; then
    echo "✓ llama3.2:3b model already present"
else
    echo "  Pulling llama3.2 models (this may take a few minutes)..."
    ollama pull llama3.2:3b
    ollama pull llama3.2:latest
    ollama pull llama3.2:1b
    echo "✓ llama3.2 models downloaded"
fi
echo ""

# Step 5: Display status
echo "========================================"
echo "Status: Ollama Ready for Labs"
echo "========================================"
echo ""
echo "Available models:"
ollama list
echo ""
echo "Ollama API endpoint: http://localhost:11434"
echo "Ollama PID: $OLLAMA_PID"
echo ""

echo ""
echo "To stop Ollama later, run:"
echo "  kill $OLLAMA_PID"
echo "  or use: pkill ollama"
echo ""

# Step 7: Stop Ollama process to allow postAttach command to restart it
echo "Stopping Ollama process ($OLLAMA_PID) so it can be managed by postAttach in devcontainer.json..."
kill $OLLAMA_PID
sleep 1
if ps -p $OLLAMA_PID > /dev/null 2>&1; then
    echo "  Ollama did not exit cleanly, forcing kill..."
    kill -9 $OLLAMA_PID
else
    echo "✓ Ollama process stopped"
fi
echo ""

echo "Ready for lab exercises! (Ollama will be started automatically by devcontainer postAttach)"
echo "========================================" 
