# trip_server.py - Multi Round-Trip Requests (MRTR), SEP-2322
# FastMCP 4.x / MCP specification revision 2026-07-28
#
# WHAT MRTR IS
#   A tool sometimes needs something mid-call: a confirmation, a missing
#   parameter, a choice. The server never initiates that exchange -- pushing
#   requests to a client would need a live two-way connection, which would pin
#   that client to one instance. It RESPONDS with resultType
#   "input_required", naming what it needs. The client gathers the answers and
#   RE-SENDS the original request -- with a NEW JSON-RPC id -- carrying
#   `inputResponses` and echoing `requestState`. Because everything the server
#   needs travels in that retry, the retry can land on a different server
#   instance and still work.
#
#   Only tools/call, resources/read and prompts/get may return input_required.
#
# THE GUARD PATTERN
#   This tool is called twice for one logical operation and branches on whether
#   answers are present. (ctx.elicit() RAISES on a 2026-07-28 connection - the
#   guard pattern is what replaces it.)
#
# requestState
#   An opaque server-owned blob. The client MUST echo it back untouched and
#   MUST NOT parse it. FastMCP integrity-protects it for you when you pass
#   RequestStateSecurity with a signing key. Every replica must share that key,
#   or a retry that lands on a different replica is rejected.

import os

from mcp.server.request_state import RequestStateSecurity
from mcp_types import ElicitRequest, ElicitRequestFormParams, InputRequiredResult

from fastmcp import Context, FastMCP

# A real deployment reads this from a secret manager and shares it across all
# replicas. 32+ bytes.
SIGNING_KEY = os.getenv("REQUEST_STATE_KEY", "lab-demo-key-not-for-production!!").encode()

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
    """Book a flight. Asks who is travelling and which flight they want.

    Returning an InputRequiredResult is what triggers another round trip;
    returning anything else ends the call.
    """

    # ctx.input_responses is None on the FIRST call and populated on the retry.
    answers = ctx.input_responses

    dest = destination.strip().lower()
    if dest not in FLIGHTS:
        return f"Sorry, we do not fly to {destination}."

    # ---- First call: no answers yet, so ask for them ---------------------
    # TODO: return an InputRequiredResult with result_type="input_required"
    #       and two input_requests keyed "traveler" and "flight":
    #         - "traveler": an ElicitRequest asking for a name (string)
    #         - "flight":   an ElicitRequest asking to pick one of FLIGHTS[dest]
    #       Pass request_state=ctx.request_state or "".

    # ---- Second call: the answers came back ------------------------------
    # TODO: read answers["traveler"] and answers["flight"], check that each has
    #       action == "accept" AND non-empty content (a user may decline), then
    #       return the confirmation string.


if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
