#!/usr/bin/env bash

set -e

# 1. Ensure CODESPACE_NAME is defined
if [ -z "$CODESPACE_NAME" ]; then
  echo "❌ CODESPACE_NAME is not set."
  exit 1
fi

# 2. Install npm if needed
if ! command -v npm &>/dev/null; then
  echo "📦 npm not found. Installing..."

  if [[ "$(uname)" == "Darwin" ]]; then
    if ! command -v brew &>/dev/null; then
      echo "❌ Homebrew not found. Please install it manually."
      exit 1
    fi
    brew install node
  elif command -v apt &>/dev/null; then
    sudo apt-get update
    sudo apt-get install -y nodejs npm
  else
    echo "❌ Unsupported platform. Please install Node.js manually."
    exit 1
  fi
else
  echo "✅ npm is already installed."
fi

# 3. Install npx (should already be included with npm ≥5.2.0)
if ! command -v npx &>/dev/null; then
  echo "🔧 Installing npx..."
  npm install -g npx
else
  echo "✅ npx is already available."
fi

# 4. Start the MCP Inspector
MCP_URL="https://${CODESPACE_NAME}-8000.app.github.dev/mcp/"
echo "🚀 Launching MCP Inspector for: $MCP_URL"

npx @modelcontextprotocol/inspector --url "$MCP_URL" --protocol streaming-http

