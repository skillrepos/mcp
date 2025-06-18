import asyncio
from fastmcp import Client

async def main():
    # 1. Point at your server’s SSE endpoint
    #    adjust host/port/path as needed
    async with Client("http://127.0.0.1:8000/mcp/") as client:
        # 2. List available tools
        tools = await client.list_tools()
        print("Available tools:", [t.name for t in tools])

        # 3. Call the weather tool
        result = await client.call_tool(
            "get_current_weather",
            {"latitude": 40.71, "longitude": -74.01}
        )

        # 4. Print out the returned temperature & wind speed
        #    result is a list of TextContent objects
        weather = result[0].text
        print(f"Weather response: {weather}")

if __name__ == "__main__":
    asyncio.run(main())