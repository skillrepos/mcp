# discover_tools.py
import asyncio
from fastmcp import Client

async def main():
    async with Client("http://127.0.0.1:9000/mcp") as c:
        tools = await c.list_tools()
        for t in tools:
            print(t.name, "—", t.description)
asyncio.run(main())
