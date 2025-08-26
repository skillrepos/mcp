#!/usr/bin/env bash

# This script sets up the Python environment and Ollama as intended by the postcreate commands

set -e

echo "Starting manual environment setup..."

# Set up Python environment
echo "Setting up Python virtual environment..."
PYTHON_ENV="py_env"

python3 -m venv ./$PYTHON_ENV \
    && export PATH=./$PYTHON_ENV/bin:$PATH \
    && grep -qxF "source $(pwd)/$PYTHON_ENV/bin/activate" ~/.bashrc || echo "source $(pwd)/$PYTHON_ENV/bin/activate" >> ~/.bashrc

source ./$PYTHON_ENV/bin/activate

echo "Installing Python dependencies..."
if [ -f "./requirements.txt" ]; then
  pip3 install -r "./requirements.txt"
else
  pip3 install -r "/workspaces/mcp/requirements/requirements.txt"
fi

# Set up Ollama
echo "Installing Ollama..."
curl -fsSL https://ollama.com/install.sh | sh

echo "Starting Ollama service..."
ollama serve &
pid=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
while ! pgrep -f "ollama"; do
  sleep 0.1
done

sleep 15


echo "Pulling llama3.2 model..."
ollama pull llama3.2
ollama list



echo "Setup complete!"
echo "Python environment: $PYTHON_ENV"
echo "To activate the environment, run: source ./$PYTHON_ENV/bin/activate"
