# note_server.py – FastMCP 3.x note-taking MCP server
# Demonstrates: tools with state, static resources, resource templates, prompts
import json
from fastmcp import FastMCP

server = FastMCP("NoteService")

# ─── In-memory note store ────────────────────────────────────────────
notes: dict[str, str] = {}

# ─── Tools ───────────────────────────────────────────────────────────

@server.tool()
def save_note(title: str, content: str) -> str:
    """Save a note with a title and content."""
    notes[title] = content
    return f"Saved note: {title}"


@server.tool()
def list_notes() -> dict:
    """List all saved note titles and count."""
    return {"notes": list(notes.keys()), "count": len(notes)}


# ─── Static resource ────────────────────────────────────────────────
# Returns a catalog of all notes (titles + previews).
# URI is fixed — always returns the full collection.

@server.resource("resource://notes/catalog")
def notes_catalog() -> str:
    """Full catalog of all stored notes."""
    return json.dumps({
        "notes": {
            k: (v[:80] + "…") if len(v) > 80 else v
            for k, v in notes.items()
        },
        "count": len(notes),
    }, indent=2)


# ─── Resource template (dynamic URI) ────────────────────────────────
# The {title} placeholder is resolved from the URI at request time.
# e.g. resource://notes/meeting-summary → title="meeting-summary"

@server.resource("resource://notes/{title}")
def get_note(title: str) -> str:
    """Retrieve a single note by its title."""
    if title == "catalog":
        return json.dumps({"error": "Use resource://notes/catalog for the full catalog."})
    if title not in notes:
        return json.dumps({"error": f"Note '{title}' not found"})
    return json.dumps({"title": title, "content": notes[title]}, indent=2)


# ─── Prompt ──────────────────────────────────────────────────────────

@server.prompt("summarize_notes")
def summarize_notes() -> str:
    """Ask an LLM to summarize all stored notes."""
    if not notes:
        return "No notes have been saved yet."
    all_notes = "\n\n".join(f"## {k}\n{v}" for k, v in notes.items())
    return f"Please provide a concise summary of the following notes:\n\n{all_notes}"


# ─── Entry point ─────────────────────────────────────────────────────

if __name__ == "__main__":
    server.run(transport="streamable-http")
