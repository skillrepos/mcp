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
python mcp_travel_server.py
