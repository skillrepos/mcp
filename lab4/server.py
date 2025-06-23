# server.py

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message=".*websockets\\.legacy.*")
warnings.filterwarnings("ignore", category=DeprecationWarning,
                        message=".*WebSocketServerProtocol is deprecated.*")

from fastmcp import FastMCP
import uvicorn

mcp = FastMCP("Calc API")


# ── 1) Raw implementation, untouched by FastMCP  ────────────────────
def _add_impl(a: int, b: int) -> int:
    return a + b


# ── 2) Expose v1 under its own name ───────────────────────────────
@mcp.tool(name="add_v1", description="Add two ints – v1")
def add_v1(a: int, b: int) -> int:
    # delegate to the raw helper
    return _add_impl(a, b)


# ── 3) Alias "add" that points at v1  ────────────────────────────
@mcp.tool(name="add", description="Add two ints (current version)")
def add(a: int, b: int) -> int:
    # again call the raw helper directly
    return _add_impl(a, b)


# ── 4) Register & capture the FastAPI app  ───────────────────────
app = mcp.streamable_http_app(path="/mcp")  # or transport="http" on FastMCP ≥2.3.2

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
