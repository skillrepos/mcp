# mcp_travel_server.py
"""
TravelHelper - FastMCP 4.x demo, MCP specification revision 2026-07-28
Serves Streamable HTTP at http://localhost:8000/mcp

What changed for the 2026-07-28 spec:
  * The endpoint is /mcp with no trailing slash. There is no session to open
    or close: every POST is a complete, independent request.
  * cache_ttl / cache_scope add the SEP-2549 caching hints (ttlMs, cacheScope)
    to tools/list, prompts/list, resources/list, resources/templates/list and
    resources/read, so clients and proxies can safely reuse results.
  * The old GET-based SSE stream is gone. Servers push change notifications
    only to clients that explicitly opened a subscriptions/listen stream.
"""
import json
import math
import os

import uvicorn

from fastmcp import FastMCP

# ──────────────────────────────────────────────────────────────
# 1)  Create the server
#     cache_ttl is in SECONDS in FastMCP; it is emitted on the wire as
#     ttlMs (milliseconds). cache_scope "public" means the response holds
#     no user-specific data and may be shared across callers and proxies.
#     Use "private" for anything that varies by authenticated user.
# ──────────────────────────────────────────────────────────────
server = FastMCP(
    "TravelHelper",
    instructions="Travel utilities: distances between cities and currency conversion.",
    cache_ttl=300,            # -> ttlMs: 300000
    cache_scope="public",
)


# ──────────────────────────────────────────────────────────────
# 2)  Tools
# ──────────────────────────────────────────────────────────────
@server.tool
def distance_between(lat1: float, lon1: float, lat2: float, lon2: float) -> dict:
    """Great-circle distance in kilometres (Haversine)."""
    p1, l1, p2, l2 = map(math.radians, (lat1, lon1, lat2, lon2))
    a = (
        math.sin((p2 - p1) / 2) ** 2
        + math.cos(p1) * math.cos(p2) * math.sin((l2 - l1) / 2) ** 2
    )
    km = 2 * 6371.0 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return {"distance_km": round(km, 2)}


@server.tool
def convert_currency(amount_usd: float, target_currency: str) -> dict:
    """Tiny demo FX table - *not* real rates."""
    rates = {"EUR": 0.90, "JPY": 140.0, "GBP": 0.80}
    code = target_currency.upper()
    if code not in rates:
        raise ValueError(f"Unsupported currency: {code}")
    return {"amount": round(amount_usd * rates[code], 2), "currency": code}


# ──────────────────────────────────────────────────────────────
# 3)  Resource  (URI must parse as a URL, so give it a scheme)
# ──────────────────────────────────────────────────────────────
@server.resource("resource://major_cities")
def major_cities() -> str:
    """Static list of cities with coordinates."""
    return json.dumps(
        {
            "cities": [
                {"name": "Paris", "lat": 48.8566, "lon": 2.3522},
                {"name": "Tokyo", "lat": 35.6895, "lon": 139.6917},
                {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            ]
        },
        indent=2,
    )


# ──────────────────────────────────────────────────────────────
# 4)  Prompt
# ──────────────────────────────────────────────────────────────
@server.prompt("recommend_sightseeing")
def recommend_sightseeing(city: str) -> str:
    """You are a travel guide. List the top 3 attractions in the given city."""
    return f"You are a travel guide. List the top 3 attractions in {city}, one per line."


# ──────────────────────────────────────────────────────────────
# 5)  Run
#     http_app() builds a Starlette app so we can control CORS for the
#     browser-based Explorer. allowed_origins also feeds the Origin-header
#     validation the spec requires as DNS-rebinding protection.
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    allowed = os.getenv("ALLOWED_ORIGINS", "*").split(",")
    app = server.http_app(path="/mcp", allowed_origins=allowed)
    uvicorn.run(app, host="0.0.0.0", port=8000)
