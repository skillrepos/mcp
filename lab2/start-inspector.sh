export DANGEROUSLY_OMIT_AUTH=true
export MCP_PROXY_FULL_ADDRESS=https://${CODESPACE_NAME}-6277.app.github.dev
export ALLOWED_ORIGINS=https://${CODESPACE_NAME}-6274.app.github.dev,https://${CODESPACE_NAME}-6277.app.github.dev
( 
    sleep 15
    gh codespace ports visibility --codespace $CODESPACE_NAME 8000:public 6274:public 6277:public 8000:public
    echo Inspector is available at https://${CODESPACE_NAME}-6274.app.github.dev
) &
npx --yes @modelcontextprotocol/inspector   --config mcp.json   --server codespace
