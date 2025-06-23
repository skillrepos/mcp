# server_v2.py

from fastmcp import FastMCP
import uvicorn

mcp = FastMCP("Calc API")

# ── Core implementation helpers ───────────────────────────────────
def _sub_impl_v1(a: int, b: int) -> int:
    return a - b

def _sub_impl_v2(a: int, b: int) -> int:
    return b - a

# ── Versioned tools ───────────────────────────────────────────────
@mcp.tool(name="sub_v1", description="sub two ints – v1")
def sub_v1(a: int, b: int) -> int:
    return _sub_impl_v1(a, b)

@mcp.tool(name="sub_v2", description="sub two ints - v2")
def sub_v2(a: int, b: int) -> str:
    return _sub_impl_v2(a, b)

# ── Alias for “current” version ───────────────────────────────────
@mcp.tool(name="sub", description="sub two ints (current version)")
def sub(a: int, b: int) -> int | str:
    # Switch here between v1 & v2
    return _sub_impl_v2(a, b)   # currently pointing at v2

# ── Register & capture the FastAPI app via streamable HTTP ─────────
app = mcp.http_app(path="/mcp", transport="http")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
