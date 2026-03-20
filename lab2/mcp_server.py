# Updated 2026-03-20: Migrated from mcp.server.fastmcp to fastmcp 3.x
import requests
from fastmcp import FastMCP

mcp = FastMCP("WeatherService")

@mcp.tool()
def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    Returns:
      temperature_2m (°C), wind_speed_10m (m/s)
    """
    url = (
      "https://api.open-meteo.com/v1/forecast"
      "?latitude={lat}&longitude={lon}"
      "&current_weather=true"
    ).format(lat=latitude, lon=longitude)
    resp = requests.get(url)
    resp.raise_for_status()
    cw = resp.json()["current_weather"]
    return {
      "temperature_2m": cw["temperature"],
      "wind_speed_10m": cw["windspeed"]
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")