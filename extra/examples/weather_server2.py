# weather_server2.py - FastMCP 4.x / MCP specification revision 2026-07-28
# Same as weather_server.py but reports imperial units.
import requests

from fastmcp import FastMCP

mcp = FastMCP("WeatherService", cache_ttl=300, cache_scope="public")


@mcp.tool
def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    Current weather for a coordinate.

    Returns:
      temperature_2m (deg F), wind_speed_10m (mph)
    """
    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={latitude}&longitude={longitude}"
        "&current_weather=true"
    )
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    cw = resp.json()["current_weather"]
    return {
        "temperature_2m": round(cw["temperature"] * 9 / 5 + 32, 1),
        "wind_speed_10m": round(cw["windspeed"] * 2.23694, 1),
    }


if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)
