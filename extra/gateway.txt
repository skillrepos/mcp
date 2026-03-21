# gateway.py – Compose multiple MCP servers behind a single endpoint
# Demonstrates FastMCP server composition with mount() and namespacing

from fastmcp import FastMCP

# Import the two servers we built
from note_server import server as note_service
from math_server import math   as math_service

# Create the gateway and mount both servers with namespaces
gateway = FastMCP("Gateway")
gateway.mount(note_service, namespace="notes")
gateway.mount(math_service, namespace="math")

# Now all tools are available at one endpoint:
#   notes_save_note, notes_list_notes
#   math_add, math_multiply
# And all resources/prompts from note_service are also available.

if __name__ == "__main__":
    gateway.run(transport="streamable-http")
