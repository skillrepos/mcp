# Kill processes on port 6274
kill -9 $(lsof -t -i:6274) 2>/dev/null

# Kill processes on port 6277
kill -9 $(lsof -t -i:6277) 2>/dev/null

export DANGEROUSLY_OMIT_AUTH=true
export MCP_PROXY_FULL_ADDRESS="https://${CODESPACE_NAME}-6277.app.github.dev"
export ALLOWED_ORIGINS="https://${CODESPACE_NAME}-6274.app.github.dev,https://${CODESPACE_NAME}-6277.app.github.dev"

echo "\n\n"
echo URL= "https://${CODESPACE_NAME}-6274.app.github.dev/?transport=streamable-http&serverUrl=https://${CODESPACE_NAME}-8000.app.github.dev/mcp/&MCP_PROXY_FULL_ADDRESS=https://${CODESPACE_NAME}-6277.app.github.dev"
echo "\n\n"


npx --yes @modelcontextprotocol/inspector 

# source start-inspector.sh
# gh codespace ports visibility --codespace $CODESPACE_NAME 8000:public 6274:public 6277:public
