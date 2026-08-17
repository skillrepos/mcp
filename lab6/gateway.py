# gateway.py - Compose multiple MCP servers behind a single endpoint
# FastMCP 4.x / MCP specification revision 2026-07-28
#
# Note: mount() takes `namespace=` in FastMCP 4 (it was `prefix=` in 3.x).

from fastmcp import FastMCP

# TODO: Import the two servers we built (note_server and math_server)

# TODO: Create the gateway and mount both servers with namespaces


if __name__ == "__main__":
    gateway.run(transport="http", host="0.0.0.0", port=8000)
