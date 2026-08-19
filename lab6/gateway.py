# gateway.py - Compose multiple MCP servers behind a single endpoint
# FastMCP 4.x / MCP specification revision 2026-07-28
#
# Note: mount() takes `namespace=` in FastMCP 4 (it was `prefix=` in 3.x).

from fastmcp import FastMCP

# 1) Import the two servers we built. These are ordinary Python objects,
#    so composing them needs no network hop.
# TODO: import note_server's `server` as note_service, and math_server's
#       `math_service`

# 2) Create the gateway, then mount both servers under namespaces.
# TODO: create the gateway, then mount note_service under "notes" and
#       math_service under "math"

# Tools are then exposed as notes_open_notebook, notes_save_note,
# notes_list_notes, math_add and math_multiply.

if __name__ == "__main__":
    gateway.run(transport="http", host="0.0.0.0", port=8000)
