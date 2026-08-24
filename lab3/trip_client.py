# trip_client.py - the client half of Multi Round-Trip Requests
# FastMCP 4.x / MCP specification revision 2026-07-28
#
# Register an elicitation_handler and FastMCP drives the whole MRTR loop for
# you: it sees resultType "input_required", calls your handler once per
# requested input, then re-sends the original tools/call with a new JSON-RPC id,
# the answers in `inputResponses`, and `requestState` echoed back verbatim.
#
# The same handler also answers server-pushed elicitations on legacy
# connections, so one handler covers both protocol eras.

import asyncio

from fastmcp import Client
from fastmcp.client.elicitation import ElicitResult

SERVER_URL = "http://127.0.0.1:8000/mcp"


async def elicitation_handler(message, response_type, params, context):
    """Called once for each input the server asks for.

    In a real host this is where you would render UI and wait for the user.
    Here we read from the terminal so you can watch the round trips happen.

    Return a dict to accept, or ElicitResult(action="decline") to refuse.
    The spec requires servers to handle a refusal gracefully - a user is
    always allowed to say no.
    """
    print(f"\n  [server is asking] {message}")

    schema = getattr(params, "requested_schema", None) or {}
    props = schema.get("properties", {})
    field = next(iter(props), None)
    if field is None:
        return {}

    options = props[field].get("enum")
    if options:
        for i, opt in enumerate(options, 1):
            print(f"    {i}. {opt}")
        raw = input("  Choose a number: ").strip()
        try:
            return {field: options[int(raw) - 1]}
        except (ValueError, IndexError):
            print("  Invalid choice - declining.")
            return ElicitResult(action="decline")

    return {field: input(f"  {field}: ").strip()}


async def main():
    async with Client(SERVER_URL, elicitation_handler=elicitation_handler) as client:
        print("Negotiated protocol version:", client.protocol_version)
        print("\nCalling book_trip('Paris')...")
        print("Watch the server log: you will see MORE THAN ONE POST for this")
        print("single logical call. That is MRTR - each round trip is an")
        print("independent request that could hit a different server instance.\n")

        result = await client.call_tool("book_trip", {"destination": "Paris"})
        print("\nFinal result:", result.data or result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())
