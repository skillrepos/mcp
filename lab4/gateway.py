# gateway.py – Compose multiple MCP servers behind a single endpoint
# Demonstrates FastMCP server composition with mount() and namespacing

from fastmcp import FastMCP

# TODO: Import the two servers we built (note_server and math_server)

# TODO: Create the gateway and mount both servers with namespaces

if __name__ == "__main__":
    gateway.run(transport="streamable-http")
