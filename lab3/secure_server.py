# secure_server.py  – FastMCP ≥ 2.3
# Provides a single "add" tool protected by bearer-token auth (JWT).

import warnings
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from jose import jwt, JWTError

from fastmcp import FastMCP
import uvicorn

warnings.filterwarnings("ignore", category=DeprecationWarning)

# ─── JWT settings (must match auth_server.py) ─────────────────────────────
SECRET_KEY = "mcp-lab-secret"
ALGORITHM  = "HS256"
AUDIENCE   = "mcp-lab"
# ──────────────────────────────────────────────────────────────────────────

# 1) Create the MCP server
mcp = FastMCP("Secure Calc")

# 2) Mount both HTTP POST & SSE GET on /mcp
app = mcp.http_app(path="/mcp", transport="streamable-http")


# 3) Auth middleware – verify JWT locally
class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path.startswith("/mcp"):
            auth = request.headers.get("authorization", "")
            if not auth.startswith("Bearer "):
                raise HTTPException(status_code=401, detail="Missing token")

            token = auth.removeprefix("Bearer ").strip()
            try:
                jwt.decode(token, SECRET_KEY,
                           algorithms=[ALGORITHM], audience=AUDIENCE)
            except JWTError as exc:
                raise HTTPException(status_code=401,
                                    detail=f"Token invalid: {exc}")
        return await call_next(request)


# 4) Register the middleware
app.add_middleware(AuthMiddleware)


# 5) Secure tool
@mcp.tool(description="Secure add")
async def add(a: int, b: int) -> int:
    return a + b


# 6) Run
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
