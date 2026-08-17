# start-inspector.sh
# Updated 2026-08-03 for MCP specification revision 2026-07-28.
#   * The endpoint is /mcp with no trailing slash.
#   * Requires MCP Inspector 2.x, which is the first line to support the
#     2026-07-28 revision. `npx --yes` below always fetches the latest.
#   * The Explorer (scripts/mcp_explorer.py) is the tool used in the labs;
#     this script is here if you prefer the official Inspector.

# Kill processes on port 6274
kill -9 $(lsof -t -i:6274) 2>/dev/null

# Kill processes on port 6277
kill -9 $(lsof -t -i:6277) 2>/dev/null

sleep 5

export DANGEROUSLY_OMIT_AUTH=true
export ALLOWED_ORIGINS="https://${CODESPACE_NAME}-6274.app.github.dev,https://${CODESPACE_NAME}-6277.app.github.dev"
export MI_URL="https://${CODESPACE_NAME}-6274.app.github.dev/?transport=streamable-http&serverUrl=https://${CODESPACE_NAME}-8000.app.github.dev/mcp&MCP_PROXY_FULL_ADDRESS=https://${CODESPACE_NAME}-6277.app.github.dev"

echo ""
echo ""
echo To open the inspector...
echo ""
echo "    1. Wait until the next command tells you the inspector is up and running"
echo ""
echo "    2. In the PORTS tab (next to TERMINAL) on the rows for 6274 and 6277, right-click and Set Visibility to Public"
echo ""
echo "    3. Open the app at the URL printed below"
echo ""
echo         $MI_URL
echo ""
echo ""


npx --yes @modelcontextprotocol/inspector@latest

