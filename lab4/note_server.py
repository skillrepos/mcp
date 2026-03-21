# note_server.py – FastMCP 3.x note-taking MCP server
# Demonstrates: tools with state, static resources, resource templates, prompts
from fastmcp import FastMCP

server = FastMCP("NoteService")

# ─── In-memory note store ────────────────────────────────────────────
notes: dict[str, str] = {}

# ─── Tools ───────────────────────────────────────────────────────────

# TODO: save_note tool – save a note with title and content

# TODO: list_notes tool – list all saved note titles and count


# ─── Static resource ────────────────────────────────────────────────
# TODO: notes_catalog resource at resource://notes/catalog


# ─── Resource template (dynamic URI) ────────────────────────────────
# TODO: get_note resource template at resource://notes/{title}


# ─── Prompt ──────────────────────────────────────────────────────────

# TODO: summarize_notes prompt


# ─── Entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    server.run(transport="streamable-http")
