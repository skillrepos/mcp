#!/usr/bin/env python3
"""
discover_tools.py
────────────────────────────────────────────────────────────────────
Connect to a running MCP server and print a summary of everything it
exposes: supported protocol versions, capabilities, and each tool.

Updated 2026-08-03 for MCP specification revision 2026-07-28.

What changed:
  * There is no initialize handshake to perform first. The client either calls
    server/discover or simply sends the request it wants.
  * Tool schema fields are snake_case in the SDK (input_schema, output_schema);
    they are still inputSchema / outputSchema on the wire.
  * List results now carry ttlMs / cacheScope caching hints.

Usage
-----
python discover_tools.py [port] [path]

Arguments:
  port  - Port number (default: 8000)
  path  - Endpoint path without a leading slash (default: mcp)

Example:
  python discover_tools.py 8931 mcp
  # Connects to http://127.0.0.1:8931/mcp
"""

import asyncio
import re
import sys

from fastmcp import Client

CYAN = "\033[96m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
MAGENTA = "\033[95m"
RESET = "\033[0m"


async def main(port: int = 8000, path: str = "mcp") -> None:
    # No trailing slash: /mcp is the canonical 2026-07-28 endpoint form.
    url = f"http://127.0.0.1:{port}/{path}"
    print(f"Connecting to: {url}")

    # mode="auto" (the default) speaks 2026-07-28 where available and falls
    # back to the legacy initialize handshake for older servers.
    async with Client(url) as mcp:
        print(f"\n{CYAN}Protocol version negotiated:{RESET} {mcp.protocol_version}")
        info = mcp.server_info
        if info:
            print(f"{CYAN}Server:{RESET} {info.name} {info.version or ''}")
        if mcp.instructions:
            print(f"{CYAN}Instructions:{RESET} {mcp.instructions}")
        if mcp.server_capabilities:
            print(f"{CYAN}Capabilities:{RESET} {mcp.server_capabilities}")

        tools = await mcp.list_tools()
        print(f"\nDiscovered {len(tools)} tool(s):\n")

        for i, tool in enumerate(tools, start=1):
            print(CYAN + "-" * 70 + RESET)
            print(CYAN + f"Tool {i}: {tool.name}" + RESET)
            print(CYAN + "-" * 70 + RESET)
            print()

            description = tool.description or ""
            description = re.split(
                r"\n\s*(Parameters|Returns)\s*\n\s*[-=]+\s*\n",
                description,
                flags=re.IGNORECASE,
            )[0].strip()

            print(CYAN + "Description" + RESET)
            print(CYAN + "-----------" + RESET)
            print(GREEN + (description or "(none)") + RESET)
            print()

            # SDK v2 exposes this as input_schema (inputSchema on the wire).
            schema = getattr(tool, "input_schema", None)
            if schema:
                print(CYAN + "Parameters" + RESET)
                print(CYAN + "----------" + RESET)
                props = schema.get("properties", {})
                if props:
                    required = schema.get("required", [])
                    for name, info in props.items():
                        ptype = info.get("type", "any")
                        pdesc = info.get("description", "No description")
                        req = " (required)" if name in required else ""
                        print(YELLOW + f"  {name}: {ptype}{req}" + RESET)
                        print(YELLOW + f"    {pdesc}" + RESET)
                else:
                    print(YELLOW + "  No parameters" + RESET)
                print()

            out = getattr(tool, "output_schema", None)
            if out:
                print(CYAN + "Returns" + RESET)
                print(CYAN + "-------" + RESET)
                print(MAGENTA + str(out) + RESET)
                print()


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    path = sys.argv[2] if len(sys.argv) > 2 else "mcp"
    asyncio.run(main(port, path))
