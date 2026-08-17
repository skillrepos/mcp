# trip_server.py - Multi Round-Trip Requests (MRTR), SEP-2322
# FastMCP 4.x / MCP specification revision 2026-07-28
#
# THE PROBLEM MRTR SOLVES
#   Before 2026-07-28, a server that needed something from the client mid-call
#   sent a JSON-RPC *request* back down an SSE stream it was holding open. That
#   requires a live bidirectional connection, which requires session affinity,
#   which is exactly what the stateless redesign removed.
#
#   Under MRTR the server never initiates anything. It RESPONDS with
#   resultType "input_required", naming what it needs. The client gathers the
#   answers and RE-SENDS the original request with a NEW id, carrying
#   `inputResponses` and echoing `requestState`.
#
#   Only tools/call, resources/read and prompts/get may return input_required.
#
# NOTE: ctx.elicit() still works on legacy connections but RAISES on
# 2026-07-28 connections. The modern shape is the "guard pattern": the tool is
# called twice and branches on whether answers are present.

import os

from mcp.server.request_state import RequestStateSecurity
from mcp_types import ElicitRequest, ElicitRequestFormParams, InputRequiredResult

from fastmcp import Context, FastMCP

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
    """Book a flight. Asks who is travelling and which flight they want."""

    # ctx.input_responses is None on the FIRST call, populated on the retry.
    answers = ctx.input_responses

    dest = destination.strip().lower()
    if dest not in FLIGHTS:
        return f"Sorry, we do not fly to {destination}."

    # ---- Round 1: no answers yet ----------------------------------------
    # TODO: return an InputRequiredResult with result_type="input_required"
    #       and two input_requests keyed "traveler" and "flight":
    #         - "traveler": an ElicitRequest asking for a name (string)
    #         - "flight":   an ElicitRequest asking to pick one of FLIGHTS[dest]
    #       Pass request_state=ctx.request_state or "".

    # ---- Round 2: the client re-sent the call with the answers -----------
    # TODO: read answers["traveler"] and answers["flight"], check that each
    #       has action == "accept" AND non-empty content (a user may decline),
    #       then return the confirmation string.


if __name__ == "__main__":
    server.run(transport="http", host="0.0.0.0", port=8000)
