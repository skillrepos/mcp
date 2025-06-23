# secure_client.py  – FastMCP ≥ 2.3
# 1) Obtains a bearer token from the auth server
# 2) Uses it to call the secure 'add' tool on the MCP server

import asyncio
import httpx
from fastmcp import Client

AUTH_SERVER  = "http://127.0.0.1:9000/token"
MCP_ENDPOINT = "http://127.0.0.1:8000/mcp/"   # note trailing slash

async def main():
    # Step 1 ── get a JWT
    async with httpx.AsyncClient() as h:
        r = await h.post(
            AUTH_SERVER,
            data={"username": "demo-client", "password": "demopass",
                  "scope": "calc:add"}      # scope param ignored by our tiny AS
        )
        r.raise_for_status()
        token = r.json()["access_token"]

    # Step 2 ── call MCP with the token
    async with Client(MCP_ENDPOINT, auth=token) as c:
        tools = await c.list_tools()
        print("Available tools:", [t.name for t in tools])

        result = await c.call_tool("add", {"a": 7, "b": 5})
        print("7 + 5 =", result)

if __name__ == "__main__":
    asyncio.run(main())
