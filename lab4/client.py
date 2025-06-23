# client.py

import asyncio
from fastmcp import Client

async def main():
    # Notice: we point at /mcp/ and the Client will detect
    # streamable-HTTP and open an SSE GET under the hood.
    async with Client("http://127.0.0.1:8000/mcp/") as c:
        # 1) list tools
        tools = await c.list_tools()
        print("Available tools:", [(t.name, t.description) for t in tools])

        # 2) call the alias
        res = await c.call_tool("add", {"a": 3, "b": 4})
        print("add(3,4) ->", res)

if __name__ == "__main__":
    asyncio.run(main())
