# replica_server.py - the Lab 4 TripBooker, made replica-ready.
#
# Same MRTR tool as Lab 4, with two changes that matter for replicas:
#   * the port comes from the command line, so you can run several copies
#   * every step logs which replica handled it, so you can WATCH one logical
#     call span two machines
#
# Why this works across replicas when memory_server.py does not: TripBooker
# keeps NOTHING in process memory between the two rounds. Everything it needs
# on the retry travels inside requestState - signed by the server, carried
# (unread) by the client.
#
# The signing key comes from REQUEST_STATE_KEY, defaulting to a shared lab
# value. Every replica MUST hold the same key: replica B can only accept a
# requestState that replica A signed if they share it. Start one replica with
# a different key to see exactly how that failure looks.
#
# Usage:  python replica_server.py <port>

import os
import sys

from mcp.server.request_state import RequestStateSecurity
from mcp_types import ElicitRequest, ElicitRequestFormParams, InputRequiredResult

from fastmcp import Context, FastMCP

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8001
NAME = f"replica-{PORT}"
GREEN, BLUE, RESET = "\033[92m", "\033[94m", "\033[0m"

SIGNING_KEY = os.getenv(
    "REQUEST_STATE_KEY", "lab-demo-key-not-for-production!!"
).encode()

server = FastMCP(
    "TripBooker",
    instructions="Books a trip, asking follow-up questions across round trips.",
    request_state_security=RequestStateSecurity(keys=[SIGNING_KEY]),
)

FLIGHTS = {
    "paris": ["AF017 08:15", "DL262 17:40"],
    "tokyo": ["NH009 11:05", "JL005 13:20"],
    "london": ["BA178 09:30", "VS004 18:55"],
}


@server.tool
async def book_trip(destination: str, ctx: Context) -> str | InputRequiredResult:
    """Book a flight. Asks who is travelling and which flight they want."""
    answers = ctx.input_responses

    dest = destination.strip().lower()
    if dest not in FLIGHTS:
        return f"Sorry, we do not fly to {destination}."

    # ---- Round 1: no answers yet -> ask, and hand back signed state -------
    if answers is None:
        print(f"{BLUE}[{NAME}] round 1: asking for inputs, "
              f"returning signed requestState{RESET}")
        return InputRequiredResult(
            result_type="input_required",
            input_requests={
                "traveler": ElicitRequest(
                    method="elicitation/create",
                    params=ElicitRequestFormParams(
                        message=f"Who is travelling to {destination.title()}?",
                        requested_schema={
                            "type": "object",
                            "properties": {
                                "name": {"type": "string", "title": "Traveler name"}
                            },
                            "required": ["name"],
                        },
                    ),
                ),
                "flight": ElicitRequest(
                    method="elicitation/create",
                    params=ElicitRequestFormParams(
                        message=f"Which flight to {destination.title()}?",
                        requested_schema={
                            "type": "object",
                            "properties": {
                                "choice": {
                                    "type": "string",
                                    "title": "Flight",
                                    "enum": FLIGHTS[dest],
                                }
                            },
                            "required": ["choice"],
                        },
                    ),
                ),
            },
            request_state=ctx.request_state or "",
        )

    # ---- Round 2: this may be a DIFFERENT replica than round 1 ------------
    print(f"{GREEN}[{NAME}] round 2: verified requestState signature, "
          f"finishing the booking{RESET}")
    traveler = answers.get("traveler")
    flight = answers.get("flight")
    for name, ans in (("traveler", traveler), ("flight", flight)):
        if ans is None or getattr(ans, "action", None) != "accept" or not ans.content:
            return f"Booking cancelled: no answer given for {name}."

    who = traveler.content["name"]
    which = flight.content["choice"]
    return f"Booked {which} to {destination.title()} for {who}.  [finished on {NAME}]"


if __name__ == "__main__":
    print(f"{GREEN}[{NAME}] starting on port {PORT}  "
          f"(signing key: {'CUSTOM' if 'REQUEST_STATE_KEY' in os.environ else 'shared lab default'}){RESET}")
    server.run(transport="http", host="127.0.0.1", port=PORT)
