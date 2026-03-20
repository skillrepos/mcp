#!/usr/bin/env python3
"""
discover_tools.py
────────────────────────────────────────────────────────────────────
**Purpose**
Connect to a running FastMCP server and print a one-line summary
(name + description) of every tool the server currently exposes.

Why you might run this
----------------------
* Quick sanity-check that your MCP server is live.
* See the exact spelling of tool names before calling them.
* Share a lightweight script with teammates who don't know FastMCP yet.

Usage
-----
python discover_tools.py [port] [transport]

Arguments:
  port      - Port number (default: 8000)
  transport - Transport type (default: mcp)

Example:
  python discover_tools.py 8931 sse
  # Connects to http://127.0.0.1:8931/sse/

Assumptions
-----------
* The server is reachable at the constructed URL.
* No authentication is required (default local dev setup).
"""

import asyncio                    # built-in: run asynchronous code
import sys                        # built-in: command-line arguments
import re                         # built-in: regular expressions
from fastmcp import Client        # official async JSON-RPC wrapper

# ╔════════════════════════════════════════════════════════════════╗
# 1.  Async entry-point                                           ║
# ╚════════════════════════════════════════════════════════════════╝
async def main(port: int = 8000, transport: str = "mcp") -> None:
    """
    Open an async connection to the MCP endpoint, retrieve the list of
    tools, and print formatted information for each.

    Args:
        port: Port number for the MCP server (default: 8000)
        transport: Transport type for the connection (default: mcp)
    """
    # Construct the URL from port and transport arguments
    url = f"http://127.0.0.1:{port}/{transport}/"
    print(f"Connecting to: {url}")

    # `Client` is an asynchronous context-manager: it opens the HTTP
    # connection on entry and closes it on exit.
    async with Client(url) as mcp:

        # `list_tools()` sends a JSON-RPC request {method:"tools/list"}
        # and returns a list of Tool objects (attributes: name, description…)
        tools = await mcp.list_tools()

        # ANSI color codes
        CYAN = "\033[96m"       # Cyan for headings (tool name)
        GREEN = "\033[92m"      # Green for descriptions
        YELLOW = "\033[93m"     # Yellow for parameters
        MAGENTA = "\033[95m"    # Magenta for return information
        RESET = "\033[0m"       # Reset to default color

        # Print formatted catalogue with numbered tools
        print(f"\nDiscovered {len(tools)} tool(s):\n")

        for i, tool in enumerate(tools, start=1):
            print(CYAN + "-" * 70 + RESET)
            print(CYAN + f"Tool {i}: {tool.name}" + RESET)
            print(CYAN + "-" * 70 + RESET)
            print()

            # Description - clean up docstring sections
            description = tool.description
            # Remove "Parameters" and "Returns" sections from docstrings
            # Match patterns like "Parameters\n----------" or "Returns\n-------"
            description = re.split(r'\n\s*(Parameters|Returns)\s*\n\s*[-=]+\s*\n', description, flags=re.IGNORECASE)[0]
            description = description.strip()

            print(CYAN + "Description" + RESET)
            print(CYAN + "-----------" + RESET)
            print(GREEN + description + RESET)
            print()

            # Parameters (inputSchema)
            if hasattr(tool, 'inputSchema') and tool.inputSchema:
                print(CYAN + "Parameters" + RESET)
                print(CYAN + "----------" + RESET)
                schema = tool.inputSchema
                if 'properties' in schema:
                    for param_name, param_info in schema['properties'].items():
                        param_type = param_info.get('type', 'any')
                        param_desc = param_info.get('description', 'No description')
                        required = ' (required)' if param_name in schema.get('required', []) else ''
                        print(YELLOW + f"  {param_name}: {param_type}{required}" + RESET)
                        print(YELLOW + f"    {param_desc}" + RESET)
                else:
                    print(YELLOW + "  No parameters" + RESET)
                print()

            # Return information
            if hasattr(tool, 'returnType') and tool.returnType:
                print(CYAN + "Returns" + RESET)
                print(CYAN + "-------" + RESET)
                print(MAGENTA + str(tool.returnType) + RESET)
                print()
            elif hasattr(tool, 'outputSchema') and tool.outputSchema:
                print(CYAN + "Returns" + RESET)
                print(CYAN + "-------" + RESET)
                print(MAGENTA + str(tool.outputSchema) + RESET)
                print()

# ╔════════════════════════════════════════════════════════════════╗
# 2.  Synchronous bootstrap                                       ║
# ╚════════════════════════════════════════════════════════════════╝
# asyncio.run() creates an event-loop, executes `main()`, and
# automatically shuts everything down when `main()` finishes.
if __name__ == "__main__":
    # Parse command-line arguments
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    transport = sys.argv[2] if len(sys.argv) > 2 else "mcp"

    asyncio.run(main(port, transport))
