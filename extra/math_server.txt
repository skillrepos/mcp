# math_server.py – small MCP server with arithmetic tools
from fastmcp import FastMCP

math = FastMCP("MathService")


@math.tool()
def add(a: float, b: float) -> float:
    """Add two numbers."""
    return a + b


@math.tool()
def multiply(a: float, b: float) -> float:
    """Multiply two numbers."""
    return a * b
