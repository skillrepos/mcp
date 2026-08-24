# math_server.py - small MCP server with arithmetic tools
# FastMCP 4.x / MCP specification revision 2026-07-28
from fastmcp import FastMCP

math_service = FastMCP("MathService", cache_ttl=3600, cache_scope="public")


# TODO: add tool - add two numbers


# TODO: multiply tool - multiply two numbers


if __name__ == "__main__":
    math_service.run(transport="http", host="0.0.0.0", port=8001)
