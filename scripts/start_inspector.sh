#!/bin/bash
# Robust MCP Inspector launcher for GitHub Codespaces
set -euo pipefail

# Configurable ports (override by exporting before running)
: "${INSPECTOR_PORT:=6274}"
: "${PROXY_PORT:=6277}"
: "${SERVER_PORT:=8000}"

# Dependencies
command -v gh >/dev/null || { echo "gh CLI is required."; exit 1; }
command -v lsof >/dev/null || { echo "lsof is required."; exit 1; }
command -v npx >/dev/null || { echo "npx is required."; exit 1; }
command -v curl >/dev/null || { echo "curl is required."; exit 1; }

# Verify Codespace
: "${CODESPACE_NAME:?This script must be run inside a GitHub Codespace (CODESPACE_NAME not set).}"

# Clean up any prior inspector/proxy processes
echo "Killing any existing processes on ${INSPECTOR_PORT} and ${PROXY_PORT}..."
kill -9 $(lsof -tiTCP:${INSPECTOR_PORT},${PROXY_PORT}) 2>/dev/null || true
sleep 5

# Origins (cover both host patterns to avoid CORS flakes)
ORIGIN_APP_INSPECTOR="https://${CODESPACE_NAME}-${INSPECTOR_PORT}.app.github.dev"
ORIGIN_APP_PROXY="https://${CODESPACE_NAME}-${PROXY_PORT}.app.github.dev"
ORIGIN_PREVIEW_INSPECTOR="https://${CODESPACE_NAME}-${INSPECTOR_PORT}.preview.app.github.dev"
ORIGIN_PREVIEW_PROXY="https://${CODESPACE_NAME}-${PROXY_PORT}.preview.app.github.dev"

# Env for Inspector/Proxy; ALSO use the same value when starting your MCP server
export DANGEROUSLY_OMIT_AUTH=true
export ALLOWED_ORIGINS="${ORIGIN_APP_INSPECTOR},${ORIGIN_APP_PROXY},${ORIGIN_PREVIEW_INSPECTOR},${ORIGIN_PREVIEW_PROXY}"

# Inspector URL pointing at streamable-http MCP server and proxy
export MI_URL="${ORIGIN_APP_INSPECTOR}/?transport=streamable-http&serverUrl=https://${CODESPACE_NAME}-${SERVER_PORT}.app.github.dev/mcp&MCP_PROXY_FULL_ADDRESS=${ORIGIN_APP_PROXY}"

echo "Environment variables set for Inspector:"
echo "  DANGEROUSLY_OMIT_AUTH=${DANGEROUSLY_OMIT_AUTH:-}"
echo "  ALLOWED_ORIGINS=$ALLOWED_ORIGINS"
echo "  MI_URL=$MI_URL"
echo
echo "NOTE: If your MCP server enforces CORS via ALLOWED_ORIGINS,"
echo "      start the server with the SAME ALLOWED_ORIGINS in its environment."

# Start MCP Inspector silently and fully detach from terminal
echo "Starting MCP Inspector silently..."
nohup npx --yes @modelcontextprotocol/inspector --no-open > /dev/null 2>&1 &

# Helper: wait for ports
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

# Wait for required ports (server → proxy → inspector)
wait_for_port "${SERVER_PORT}"
wait_for_port "${PROXY_PORT}"
wait_for_port "${INSPECTOR_PORT}"

# Make all ports public to avoid background “allow” redirects
echo "Making ports public..."
gh codespace ports visibility "${SERVER_PORT}:public" "${PROXY_PORT}:public" "${INSPECTOR_PORT}:public" --codespace "$CODESPACE_NAME"

# Shorten the MI_URL using tinyurl.com (best-effort)
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
echo "If the Inspector 'Connect' button still fails:"
echo "  1) Open ${ORIGIN_APP_PROXY} and https://${CODESPACE_NAME}-${SERVER_PORT}.app.github.dev in a tab once."
echo "  2) Then click Connect again (cookies/consent now set)."