import asyncio
from fastmcp import Client

async def main():
    async with Client("http://127.0.0.1:9000/mcp/") as c:
        text = ("Model-Context Protocol (MCP) lets clients discover, version "
                "and call AI tools, prompts and resources over a simple RPC/HTTP interface.")
        out = await c.call_tool("summarize", {"text": text})
        print("Summary:", out)

asyncio.run(main())
