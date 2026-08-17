#!/usr/bin/env bash
# wire_probe.sh - look at MCP 2026-07-28 on the wire, with no SDK in the way.
#
# Usage:  ./wire_probe.sh [base-url]
# Default base URL is http://127.0.0.1:8000/mcp
#
# Everything below is a plain HTTP POST. There is no handshake to perform
# first, no session to establish, and nothing to tear down afterwards.

set -u
URL="${1:-http://127.0.0.1:8000/mcp}"
VER="2026-07-28"

# The _meta block every 2026-07-28 request must carry.
META="\"_meta\":{\"io.modelcontextprotocol/protocolVersion\":\"$VER\",\"io.modelcontextprotocol/clientInfo\":{\"name\":\"wire-probe\",\"version\":\"1.0\"},\"io.modelcontextprotocol/clientCapabilities\":{}}"

hr() { printf '\n\033[96m%s\033[0m\n' "── $1 ─────────────────────────────────────────"; }

# ---------------------------------------------------------------------------
hr "1. server/discover  (mandatory RPC; replaces the initialize handshake)"
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: $VER" \
  -H "Mcp-Method: server/discover" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"server/discover\",\"params\":{$META}}" \
  | python3 -m json.tool

# ---------------------------------------------------------------------------
hr "2. tools/list  (note ttlMs and cacheScope on the result)"
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: $VER" \
  -H "Mcp-Method: tools/list" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":2,\"method\":\"tools/list\",\"params\":{$META}}" \
  | python3 -m json.tool

# ---------------------------------------------------------------------------
hr "3. tools/call  (Mcp-Name mirrors params.name so gateways can route)"
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: $VER" \
  -H "Mcp-Method: tools/call" \
  -H "Mcp-Name: open_notebook" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":3,\"method\":\"tools/call\",\"params\":{$META,\"name\":\"open_notebook\",\"arguments\":{\"name\":\"wire-probe\"}}}" \
  | python3 -m json.tool

# ---------------------------------------------------------------------------
hr "4. HEADER MISMATCH  (Mcp-Name says one tool, the body says another)"
echo "Expect HTTP 400 and JSON-RPC error -32020 (HeaderMismatch)."
echo "This is why a gateway can trust the header: the server re-validates it."
curl -s -i -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: $VER" \
  -H "Mcp-Method: tools/call" \
  -H "Mcp-Name: list_notes" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":4,\"method\":\"tools/call\",\"params\":{$META,\"name\":\"open_notebook\",\"arguments\":{\"name\":\"wire-probe\"}}}" \
  | head -20

# ---------------------------------------------------------------------------
hr "5. UNSUPPORTED VERSION  (ask for a version that does not exist)"
echo "Expect HTTP 400 and JSON-RPC error -32022 (UnsupportedProtocolVersion),"
echo "with data.supported listing what the server does speak."
curl -s -X POST "$URL" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -H "MCP-Protocol-Version: 1999-01-01" \
  -H "Mcp-Method: tools/list" \
  -d "{\"jsonrpc\":\"2.0\",\"id\":5,\"method\":\"tools/list\",\"params\":{\"_meta\":{\"io.modelcontextprotocol/protocolVersion\":\"1999-01-01\",\"io.modelcontextprotocol/clientCapabilities\":{}}}}" \
  | python3 -m json.tool

# ---------------------------------------------------------------------------
hr "6. GET the endpoint  (the standalone SSE stream is gone)"
echo "In 2025-11-25 and earlier, GET opened a standalone SSE stream for"
echo "server-initiated messages. 2026-07-28 removed it: the endpoint takes"
echo "POST only, so expect a 4xx here (405 or 400 depending on the server)."
curl -s -o /dev/null -w "HTTP %{http_code}\n" -X GET "$URL"

echo
echo "Done. Note what never happened: no initialize, no Mcp-Session-Id,"
echo "no ordering requirement. Every call above stands entirely on its own."
