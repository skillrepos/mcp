# summarize_client.py
#
# Connects to an MCP server, calls the “summarize” tool, and prints only the
# human-readable summary text (no wrappers, no CallToolResult noise).
#
# Requirements
#   fastmcp ≥ 2.9.0
#   Python ≥ 3.9
#
# Usage
#   python summarize_client.py
#

import asyncio
from fastmcp import Client


async def main() -> None:
    async with Client("http://127.0.0.1:9000/mcp/") as c:
        text = (
            "Model-Context Protocol (MCP) lets clients discover, version "
            "and call AI tools, prompts and resources over a simple RPC/HTTP interface."
        )

        # Call the tool (may return a single CallToolResult or a streamed list)
        raw = await c.call_tool("summarize", {"text": text})

        print("Summary:")

        # Always treat the response as a list for uniform handling
        chunks = raw if isinstance(raw, list) else [raw]

        for chunk in chunks:
            # ── 1) Most common: CallToolResult with .content -> [TextContent, …]
            if hasattr(chunk, "content") and chunk.content:
                for block in chunk.content:
                    if hasattr(block, "text"):
                        print(block.text)
                    else:                      # non-text block (rare here)
                        print(block)

            # ── 2) Streamed TextContent objects
            elif hasattr(chunk, "text"):
                print(chunk.text)

            # ── 3) Primitive result wrapped in .data
            elif hasattr(chunk, "data"):
                print(chunk.data)

            # ── 4) Fallback: print whatever it is
            else:
                print(chunk)


if __name__ == "__main__":
    asyncio.run(main())
