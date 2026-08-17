# weather_server.py - FastMCP 4.x / MCP specification revision 2026-07-28
# Updated 2026-08-03: migrated to FastMCP 4; endpoint is /mcp (no trailing
# slash) and list results now carry ttlMs / cacheScope caching hints.
import requests

from fastmcp import FastMCP

mcp = FastMCP("WeatherService", cache_ttl=300, cache_scope="public")


@mcp.tool
def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    Current weather for a coordinate.

    Returns:
      temperature_2m (deg C), wind_speed_10m (m/s)
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current_weather=true"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    cw = resp.json()["current_weather"]
    return {"temperature_2m": cw["temperature"], "wind_speed_10m": cw["windspeed"]}


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
