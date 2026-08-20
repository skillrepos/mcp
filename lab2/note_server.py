# note_server.py - FastMCP 4.x note-taking MCP server
# MCP specification revision 2026-07-28
#
# Demonstrates: explicit state handles, tools that change state,
#               static resources, resource templates, and prompts.
#
# STATELESS BY DESIGN -- READ THIS FIRST
#   A server keeps nothing between requests. It must not infer anything from
#   previous requests, even on the same connection, because any request may
#   land on any instance behind a plain load balancer.
#
#   State that spans requests is referenced by an EXPLICIT HANDLE that the
#   server mints and the client passes back on every call. Note what this buys
#   you beyond scaling: the handle is an ordinary tool argument, so the model
#   can see it, reason about it, and carry it forward -- the state is visible
#   in the conversation instead of hidden in the transport.
#
# SECURITY (spec: "State Handle Hijacking")
#   Possessing a handle is NOT authentication. Handles must be unguessable and
#   bound server-side to the authenticated caller. We use secrets.token_urlsafe
#   below; a real server would additionally key the store by verified user id.

import json
import secrets
from datetime import datetime, timedelta, timezone

from fastmcp import FastMCP

server = FastMCP(
    "NoteService",
    instructions="Create a notebook, then save and read notes inside it.",
    cache_ttl=60,
    # Notebook contents differ per caller, so their cached representation
    # must not be shared across authorization contexts.
    cache_scope="private",
)

# ─── Notebook store, keyed by explicit handle ────────────────────────
# In production this would be Redis or a database shared by every replica.
# The point is that it is keyed by a value the CLIENT supplies, not by a
# connection the server happens to be holding open.
notebooks: dict[str, dict] = {}

HANDLE_TTL = timedelta(hours=1)


def _new_handle() -> str:
    """Mint a handle that cannot be guessed or enumerated."""
    # TODO: return "nb_" plus secrets.token_urlsafe(16)
    ...


def _get(handle: str) -> dict:
    """Resolve a handle to its notebook, rejecting unknown or expired ones."""
    # TODO: look up the handle in `notebooks`. Raise a clear ValueError if it
    #       is unknown, and another if it is past its "expires" time.
    ...


# ─── Tools ───────────────────────────────────────────────────────────

@server.tool
def open_notebook(name: str = "default") -> dict:
    """Create a notebook and return the handle used for all later calls.

    This is the 2026-07-28 replacement for an implicit session: the server
    mints an identifier and hands it back as ordinary data.
    """
    # TODO: mint a handle, store the notebook with its name, empty notes, and
    #       an expiry, then return the handle as ordinary data.
    ...


@server.tool
def save_note(handle: str, title: str, content: str) -> dict:
    """Save a note into the notebook identified by `handle`."""
    # TODO: resolve the handle, store the note, report the new total
    ...


@server.tool
def list_notes(handle: str) -> dict:
    """List the titles of every note in the notebook identified by `handle`."""
    # TODO: resolve the handle, return the notebook name, sorted titles, count
    ...


# ─── Static resource ────────────────────────────────────────────────
# A fixed URI that always returns the same shape. Note the exact rule:
# 2026-07-28 forbids list results from varying *per connection*, but they MAY
# still vary by the authorization presented on the request - returning only the
# tools a caller's scopes permit is explicitly allowed, because credentials are
# per-request input rather than connection state. This lab has no auth, so ours
# is simply the same for everyone.

@server.resource("resource://catalog")
def notes_catalog() -> str:
    """Catalog of open notebooks and how many notes each holds."""
    # TODO: return JSON listing each open notebook's handle, name, note count
    ...


# ─── Resource template (dynamic URI) ────────────────────────────────
# The handle travels in the URI itself, which is the resource-side equivalent
# of passing it as a tool argument: explicit, visible, and stateless.

@server.resource("resource://note/{handle}/{title}")
def get_note(handle: str, title: str) -> str:
    """Read one note out of one notebook."""
    # TODO: resolve the handle, then return the one note - raising if the
    #       title is not present
    ...


# ─── Prompt ──────────────────────────────────────────────────────────

@server.prompt("summarize_notes")
def summarize_notes(handle: str) -> str:
    """Package every note in a notebook into an LLM-ready summary prompt."""
    # TODO: resolve the handle and build one prompt string from every note
    ...


# ─── Entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
