# client.py
#
# Simple MCP client that
#   1) lists available tools
#   2) calls a chosen tool
#   3) prints the human-readable result if present, otherwise the raw data
#
# Requirements
#   fastmcp ≥ 2.9.0
#   Python ≥ 3.9
#
# Usage
#   python client.py            # calls “sub” (default)
#   python client.py add        # calls “add”
#

import sys
import asyncio
from fastmcp import Client


async def main(tool: str) -> None:
    async with Client("http://127.0.0.1:8000/mcp/") as c:
        # 1) List all tools
        print("Available tools:")
        for t in await c.list_tools():
            print(f"  • {t.name}: {t.description}")

        # 2) Invoke the requested tool
        raw = await c.call_tool(tool, {"a": 4, "b": 3})

        # 3) Prefer the first text block (if any); otherwise use structured data
        if hasattr(raw, "content") and raw.content and hasattr(raw.content[0], "text"):
            result = raw.content[0].text            # e.g. "1"
        elif hasattr(raw, "data"):
            result = raw.data                       # e.g. 1
        else:
            result = raw

        print(f"\nResult of {tool}(4,3): {result!r}")


if __name__ == "__main__":
    # pick up tool name from argv[1]; default to "sub"
    tool_name = sys.argv[1] if len(sys.argv) > 1 else "sub"
    asyncio.run(main(tool_name))

