# mcp_client.py - FastMCP 4.x client, MCP specification revision 2026-07-28
#
# What changed:
#   * The endpoint has no trailing slash: /mcp, not /mcp/.
#   * There is no initialize() call. The client sends server/discover (or just
#     sends the request it wants) and each request carries its own metadata.
#   * call_tool() returns a CallToolResult object, not a bare list of content
#     blocks. Use .data for the hydrated Python value, .content for the raw
#     content blocks, .structured_content for the JSON payload.
import asyncio

from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def main():
    # mode="auto" (the default) probes with server/discover and falls back to
    # the legacy initialize handshake for servers older than 2026-07-28.
    async with Client(SERVER_URL) as client:
        # Which protocol era did we actually end up on?
        print("Negotiated protocol version:", client.protocol_version)

        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        result = await client.call_tool(
            "distance_between",
            {"lat1": 40.71, "lon1": -74.01, "lat2": 51.51, "lon2": -0.13},
        )

        print("Structured result:", result.structured_content)
        print("Hydrated data    :", result.data)
        print("First text block :", result.content[0].text if result.content else None)


if __name__ == "__main__":
    asyncio.run(main())
