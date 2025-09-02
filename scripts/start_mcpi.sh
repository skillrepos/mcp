#!/bin/bash
# script to start up MCP Inspector from command line
# Click on URL at end to open inspector
set -e

# Kill any existing processes on ports 6274 and 6277
echo "Killing any existing processes on ports 6274 and 6277..."
kill -9 $(lsof -t -i:6274) 2>/dev/null || true
kill -9 $(lsof -t -i:6277) 2>/dev/null || true

sleep 5

# Verify that we're running inside a GitHub Codespace
if [ -z "$CODESPACE_NAME" ]; then
  echo "CODESPACE_NAME is not set. This script must be run inside a GitHub Codespace."
  exit 1
fi

# Origins (cover both host patterns to avoid CORS flakes)
ORIGIN_APP_INSPECTOR="https://${CODESPACE_NAME}-${INSPECTOR_PORT}.app.github.dev"
ORIGIN_APP_PROXY="https://${CODESPACE_NAME}-${PROXY_PORT}.app.github.dev"
ORIGIN_PREVIEW_INSPECTOR="https://${CODESPACE_NAME}-${INSPECTOR_PORT}.preview.app.github.dev"
ORIGIN_PREVIEW_PROXY="https://${CODESPACE_NAME}-${PROXY_PORT}.preview.app.github.dev"

# Env for Inspector/Proxy; ALSO use the same value when starting your MCP server
export DANGEROUSLY_OMIT_AUTH=true
export ALLOWED_ORIGINS="${ORIGIN_APP_INSPECTOR},${ORIGIN_APP_PROXY},${ORIGIN_PREVIEW_INSPECTOR},${ORIGIN_PREVIEW_PROXY}"

export MI_URL="https://${CODESPACE_NAME}-6274.app.github.dev/?transport=streamable-http&serverUrl=https://${CODESPACE_NAME}-8000.app.github.dev/mcp&MCP_PROXY_FULL_ADDRESS=https://${CODESPACE_NAME}-6277.app.github.dev"

echo "Environment variables set:"
echo "  DANGEROUSLY_OMIT_AUTH=true"
echo "  ALLOWED_ORIGINS=$ALLOWED_ORIGINS"
echo "  MI_URL=$MI_URL"

# Start MCP Inspector silently and fully detach from terminal
echo "Starting MCP Inspector silently..."
nohup npx --yes @modelcontextprotocol/inspector --no-open > /dev/null 2>&1 &

# Function to wait for a port to become available using lsof
wait_for_port() {
  local port=$1
  echo "Waiting for port $port to become available..."
  local timeout=60
  local count=0

  while ! lsof -iTCP:$port -sTCP:LISTEN -Pn >/dev/null 2>&1; do
    sleep 1
    count=$((count + 1))
    if [ "$count" -ge "$timeout" ]; then
      echo "Timeout waiting for port $port"
      return 1
    fi
  done

  echo "Port $port is now available."
}

# Wait for required ports to become available
wait_for_port 8000
wait_for_port 6277
wait_for_port 6274

# Make ports public using GitHub CLI with explicit codespace name
echo "Making ports public..."
gh codespace ports visibility 8000:public 6277:public 6274:public  --codespace "$CODESPACE_NAME"

# Shorten the MI_URL using tinyurl.com
short_url=$(curl -s "https://tinyurl.com/api-create.php?url=$MI_URL")

echo
echo "MCP Inspector is running."
if [[ "$short_url" == https://tinyurl.com/* ]]; then
  echo "Shortened URL:"
  echo "$short_url"
else
  echo "Open this URL manually in your browser:"
  echo "$MI_URL"
fi
echo
