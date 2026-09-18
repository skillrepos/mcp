# call_tool.py - call the secure server's `add` tool with (or without) a token.
#
#   python call_tool.py            no Authorization header
#   python call_tool.py $TOKEN     Authorization: Bearer $TOKEN
#
# One MCP request, tools/call add(7, 5), sent exactly the way any 2026-07-28
# client sends it. The only thing that changes between runs is the token, so
# whatever the server says back is the server's verdict on that token.

import json
import re
import sys
import textwrap

import httpx

URL = "http://127.0.0.1:8000/mcp"

BOLD, DIM, RED, GREEN, RESET = "\033[1m", "\033[2m", "\033[91m", "\033[92m", "\033[0m"


def main() -> None:
    token = sys.argv[1] if len(sys.argv) > 1 else None

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2026-07-28",
        "Mcp-Method": "tools/call",
        "Mcp-Name": "add",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"

    body = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": "add",
            "arguments": {"a": 7, "b": 5},
            "_meta": {
                "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                "io.modelcontextprotocol/clientCapabilities": {},
            },
        },
    }

    print(f"\n{BOLD}POST {URL}{RESET}   tools/call  add(7, 5)")
    if token:
        print(f"Authorization: Bearer {token[:24]}...{token[-6:]}")
    else:
        print(f"{DIM}(no Authorization header){RESET}")

    resp = httpx.post(URL, headers=headers, json=body)

    colour = GREEN if resp.status_code == 200 else RED
    print(f"\n{colour}{BOLD}HTTP {resp.status_code} {resp.reason_phrase}{RESET}")

    challenge = resp.headers.get("www-authenticate")
    if challenge:
        print("WWW-Authenticate: Bearer")
        for key, value in re.findall(r'(\w+)="([^"]*)"', challenge):
            value = textwrap.fill(value, width=80, subsequent_indent=" " * 8)
            print(f"    {key} = {value}")

    if resp.status_code == 200:
        result = _parse_result(resp)
        print(f"result: {BOLD}{result}{RESET}")
    print()


def _parse_result(resp: httpx.Response):
    """The server may answer as plain JSON or as one SSE event; handle both."""
    text = resp.text
    if resp.headers.get("content-type", "").startswith("text/event-stream"):
        text = "".join(line[5:] for line in text.splitlines() if line.startswith("data:"))
    message = json.loads(text)
    if "error" in message:
        return f"JSON-RPC error: {message['error']}"
    return message["result"].get("structuredContent", {}).get("result",
           message["result"].get("content"))


if __name__ == "__main__":
    main()
