# handle_client.py - related calls through the load balancer.
#
# Round-robin spreads consecutive requests across the replicas. Against
# memory_server.py that produces the classic production symptom: the SAME
# call with the SAME handle works on one attempt and explodes on the next,
# depending purely on which replica the load balancer happens to pick.
#
# Watch both server terminals while this runs.

import asyncio

from fastmcp import Client
from fastmcp.exceptions import ToolError

LB_URL = "http://127.0.0.1:8000/mcp"


async def main():
    async with Client(LB_URL) as client:
        print("Negotiated protocol version:", client.protocol_version)

        r = await client.call_tool("open_notebook", {"name": "lab8"})
        handle = r.data["handle"]
        print(f"\nopen_notebook -> handle {handle}  "
              f"(served by {r.data['served_by']})")

        # Two IDENTICAL calls. With two replicas behind round-robin they land
        # on different ones - so exactly one of these will fail.
        for attempt in (1, 2):
            print(f"\nattempt {attempt}: save_note with handle {handle}")
            try:
                r = await client.call_tool(
                    "save_note",
                    {"handle": handle, "title": f"note-{attempt}",
                     "content": "will this land on the right replica?"},
                )
                print(f"  OK      -> {r.data}")
            except ToolError as e:
                print(f"  FAILED  -> {e}")

        print("\nSame handle. Same call. Different replica, different outcome.")
        print("That is what in-memory state does behind a load balancer.")


if __name__ == "__main__":
    asyncio.run(main())
