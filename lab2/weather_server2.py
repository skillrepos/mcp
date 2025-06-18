import requests
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("WeatherService")

@mcp.tool()
def get_current_weather(latitude: float, longitude: float) -> dict:
    """
    Returns:
      temperature_2m (°F), wind_speed_10m (mph)
    """
    url = (
      "https://api.open-meteo.com/v1/forecast"
      "?latitude={lat}&longitude={lon}"
      "&current_weather=true"
    ).format(lat=latitude, lon=longitude)
    resp = requests.get(url)
    resp.raise_for_status()
    cw = resp.json()["current_weather"]
    # Convert Celsius to Fahrenheit and m/s to mph
    temperature_f = cw["temperature"] * 9 / 5 + 32
    windspeed_mph = cw["windspeed"] * 2.23694
    return {
      "temperature_2m": round(temperature_f, 1),   # °F
      "wind_speed_10m": round(windspeed_mph, 1)    # mph
    }

if __name__ == "__main__":
    mcp.run(transport="streamable-http")
