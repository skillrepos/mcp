# memory_server.py - the ANTI-PATTERN, on purpose.
#
# A notebook server that keeps its handles in an in-memory dict. Run ONE copy
# and it works perfectly (this is essentially Lab 2). Run TWO copies behind a
# load balancer and it breaks the moment two related calls land on different
# replicas - because the handle the client faithfully passes back refers to
# memory that only ONE replica has.
#
# That failure is the lesson. Production servers fix it by putting the store
# somewhere every replica can reach (Redis, a database), keyed user:handle.
#
# Usage:  python memory_server.py <port>

import secrets
import sys

from fastmcp import FastMCP

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
NAME = f"replica-{PORT}"
GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"

server = FastMCP("NotebookService")

# In-memory = per-process = per-REPLICA. This dict is the bug.
notebooks: dict[str, dict] = {}


@server.tool
def open_notebook(name: str = "default") -> dict:
    """Create a notebook and return its handle."""
    handle = f"nb_{secrets.token_urlsafe(8)}"
    notebooks[handle] = {"name": name, "notes": {}}
    print(f"{GREEN}[{NAME}] open_notebook -> {handle}   "
          f"(stored in THIS process's memory){RESET}")
    return {"handle": handle, "served_by": NAME}


@server.tool
def save_note(handle: str, title: str, content: str) -> dict:
    """Save a note into the notebook identified by `handle`."""
    nb = notebooks.get(handle)
    if nb is None:
        print(f"{RED}[{NAME}] save_note: UNKNOWN handle {handle} - "
              f"it lives in a different replica's memory!{RESET}")
        raise ValueError(
            f"Unknown notebook handle {handle} on {NAME}. "
            "The handle is valid - but the state behind it lives in another "
            "replica's memory. In-memory state does not survive load balancing."
        )
    nb["notes"][title] = content
    print(f"{GREEN}[{NAME}] save_note '{title}' -> {handle}{RESET}")
    return {"saved": title, "served_by": NAME, "total_notes": len(nb["notes"])}


if __name__ == "__main__":
    print(f"{GREEN}[{NAME}] starting on port {PORT} - "
          f"handles live ONLY in this process{RESET}")
    server.run(transport="http", host="127.0.0.1", port=PORT)
