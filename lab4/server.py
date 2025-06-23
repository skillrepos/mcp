# server.py

from fastmcp import FastMCP
import uvicorn

mcp = FastMCP("Calc API")

# ── Core implementation helpers ───────────────────────────────────
def _sub_impl_v1(a: int, b: int) -> int:
    return a - b

# ── Versioned tools ───────────────────────────────────────────────
@mcp.tool(name="sub_v1", description="subtract two ints – v1")
def sub_v1(a: int, b: int) -> int:
    return _sub_impl_v1(a, b)

# ── Alias for “current” version ───────────────────────────────────
@mcp.tool(name="sub", description="subtract two ints (current version)")
def sub(a: int, b: int) -> int | str:
    # Call v1
    return _sub_impl_v1(a, b)   # currently pointing at v1

# ── Register & capture the FastAPI app via streamable HTTP ─────────
app = mcp.http_app(path="/mcp", transport="http")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
