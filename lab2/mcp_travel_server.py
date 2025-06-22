# travel_server.py
"""
TravelHelper – FastMCP 2.8.1 demo
Serves via Streamable-HTTP at http://localhost:8000/mcp
"""
import os
import math
from mcp.server.fastmcp import FastMCP

# ──────────────────────────────────────────────────────────────
# 1)  Create the server
# ──────────────────────────────────────────────────────────────
server = FastMCP(service_name="TravelHelper")

# ──────────────────────────────────────────────────────────────
# 2)  Tools
# ──────────────────────────────────────────────────────────────
@server.tool()
def distance_between(lat1: float, lon1: float,
                     lat2: float, lon2: float) -> dict:
    """Great-circle distance in kilometres (Haversine)."""
    φ1, λ1, φ2, λ2 = map(math.radians, (lat1, lon1, lat2, lon2))
    a = (math.sin((φ2 - φ1) / 2) ** 2 +
         math.cos(φ1) * math.cos(φ2) * math.sin((λ2 - λ1) / 2) ** 2)
    km = 2 * 6371.0 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return {"distance_km": round(km, 2)}


@server.tool()
def convert_currency(amount_usd: float, target_currency: str) -> dict:
    """Tiny demo FX table – *not* real rates."""
    rates = {"EUR": 0.90, "JPY": 140.0, "GBP": 0.80}
    code  = target_currency.upper()
    if code not in rates:
        raise ValueError(f"Unsupported currency: {code}")
    return {"amount": round(amount_usd * rates[code], 2), "currency": code}

# ──────────────────────────────────────────────────────────────
# 3)  Resource  (URI must parse as a URL ⇒ give it a scheme)
# ──────────────────────────────────────────────────────────────
@server.resource("resource://major_cities")
def major_cities() -> dict:
    """Static list of cities with coordinates."""
    return {
        "cities": [
            {"name": "Paris",    "lat": 48.8566,  "lon":   2.3522},
            {"name": "Tokyo",    "lat": 35.6895,  "lon": 139.6917},
            {"name": "New York", "lat": 40.7128,  "lon": -74.0060},
        ]
    }

# ──────────────────────────────────────────────────────────────
# 4)  Prompt
# ──────────────────────────────────────────────────────────────
@server.prompt(
    "recommend_sightseeing",
    "You are a travel guide. List the top 3 attractions in {city}, one per line."
)
def recommend_sightseeing():
    pass  # template-driven prompt

# ──────────────────────────────────────────────────────────────
# 5)  Run  (Streamable-HTTP ⇒ plain JSON when Accept: application/json)
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
   server.run(transport="streamable-http")   
