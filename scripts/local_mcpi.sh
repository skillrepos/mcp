#!/usr/bin/env bash
# local_mcpi.sh <codespace-name>

set -e

# 1. Get codespace name
CODESPACE_NAME="$1"
if [ -z "$CODESPACE_NAME" ]; then
  echo "❌ Usage: $0 <codespace-name>"
  exit 1
fi

# 2. Kill any process on ports 6274 or 6277
echo "🛑 Killing processes on ports 6274 and 6277 (if any)..."
kill -9 $(lsof -t -i:6274) 2>/dev/null || true
kill -9 $(lsof -t -i:6277) 2>/dev/null || true

# 3. Check for npm and install if missing
if ! command -v npm &>/dev/null; then
  echo "📦 npm not found. Installing..."

  if [[ "$(uname)" == "Darwin" ]]; then
    if ! command -v brew &>/dev/null; then
      echo "❌ Homebrew not found. Please install it first."
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

# 4. Ensure npx is available
if ! command -v npx &>/dev/null; then
  echo "🔧 Installing npx..."
  npm install -g npx
else
  echo "✅ npx is already available."
fi

# 5. Start MCP Inspector
MCP_URL="https://${CODESPACE_NAME}-8000.app.github.dev/mcp/"
echo "🚀 Starting MCP Inspector for: $MCP_URL"

npx @modelcontextprotocol/inspector --url "$MCP_URL" --protocol streaming-http &

# 6. Open browser to Inspector UI
INSPECTOR_URL="http://localhost:6277"
echo "🌐 Opening browser: $INSPECTOR_URL"
if command -v open &>/dev/null; then
  open "$INSPECTOR_URL"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$INSPECTOR_URL"
else
  echo "Please open your browser and go to: $INSPECTOR_URL"
fi
