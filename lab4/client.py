# client.py

import sys
import asyncio
from fastmcp import Client

async def main(tool: str):
    async with Client("http://127.0.0.1:8000/mcp/") as c:
        # 1) List all tools with name + description
        tools = await c.list_tools()
        print("Available tools:")
        for t in tools:
            print(f"  • {t.name}: {t.description}")

        # 2) Call the requested tool
        raw = await c.call_tool(tool, {"a": 4, "b": 3})

        # 3) Unwrap TextContent-like lists if needed
        if isinstance(raw, list) and raw and hasattr(raw[0], "text"):
            result = raw[0].text
        else:
            result = raw

        print(f"\nResult of {tool}(4,3): {result!r}")

if __name__ == "__main__":
    # pick up tool from argv[1], default to "add"
    tool_name = sys.argv[1] if len(sys.argv) > 1 else "sub"
    asyncio.run(main(tool_name))
