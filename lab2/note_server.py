# note_server.py - FastMCP 4.x note-taking MCP server
# MCP specification revision 2026-07-28
#
# Demonstrates: explicit state handles, tools that change state,
#               static resources, resource templates, and prompts.
#
# WHAT CHANGED IN 2026-07-28 -- READ THIS FIRST
#   Earlier revisions let a server keep per-connection state, keyed by the
#   Mcp-Session-Id header. That header is gone. MCP is now stateless: a server
#   must not infer anything from previous requests, even on the same connection,
#   because any request may land on any instance behind a plain load balancer.
#
#   State that must span requests is now referenced by an EXPLICIT HANDLE that
#   the server mints and the client passes back on every call.

import json
import secrets
from datetime import datetime, timedelta, timezone

from fastmcp import FastMCP

server = FastMCP(
    "NoteService",
    instructions="Create a notebook, then save and read notes inside it.",
    cache_ttl=60,
    cache_scope="private",
)

# ─── Notebook store, keyed by explicit handle ────────────────────────
notebooks: dict[str, dict] = {}

HANDLE_TTL = timedelta(hours=1)


# TODO: _new_handle() - mint an unguessable handle (secrets.token_urlsafe)

# TODO: _get(handle) - look up a notebook, raising a clear error if the
#       handle is unknown or expired


# ─── Tools ───────────────────────────────────────────────────────────

# TODO: open_notebook tool - create a notebook and RETURN ITS HANDLE.
#       This is the 2026-07-28 replacement for an implicit session.

# TODO: save_note tool - takes handle, title, content

# TODO: list_notes tool - takes handle, returns the note titles


# ─── Static resource ────────────────────────────────────────────────
# TODO: notes_catalog resource at resource://catalog


# ─── Resource template (dynamic URI) ────────────────────────────────
# TODO: get_note resource template at resource://note/{handle}/{title}


# ─── Prompt ──────────────────────────────────────────────────────────

# TODO: summarize_notes prompt - takes a handle


# ─── Entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
