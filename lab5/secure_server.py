# secure_server.py - FastMCP 4.x, MCP spec revision 2026-07-28
#
# A single "add" tool protected by OAuth 2.1 bearer tokens.
#
# What changed for the 2026-07-28 spec:
#   * We no longer hand-roll ASGI middleware that just looks for a Bearer prefix.
#     FastMCP's auth providers implement the spec's required behavior for us:
#       - 401 with a WWW-Authenticate header naming the resource metadata URL
#       - RFC 9728 Protected Resource Metadata served at a well-known URL
#       - RFC 8707 audience validation (token MUST be issued FOR this server)
#       - scope enforcement, with 403 + insufficient_scope on a scope shortfall
#   * Audience validation is a MUST, not a nicety. A server that accepts a token
#     minted for someone else is the "confused deputy" the spec warns about.
#   * There is no session to protect anymore - 2026-07-28 removed Mcp-Session-Id,
#     so every request is authorized on its own, from its own Authorization header.

import uvicorn
from pydantic import AnyHttpUrl

from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier, RemoteAuthProvider

# --- Must match auth_server.py -------------------------------------------
SECRET_KEY = "mcp-lab-secret"
ALGORITHM = "HS256"
ISSUER = "http://127.0.0.1:9000"

# 1) Our canonical resource URI (RFC 8707). Tokens MUST carry this as their
#    audience. Canonical form: lowercase scheme/host, no trailing slash,
#    no fragment.
RESOURCE = "http://127.0.0.1:8000/mcp"
BASE_URL = "http://127.0.0.1:8000"
# -------------------------------------------------------------------------

# 2) The token verifier. `audience` is what enforces RFC 8707: a token whose
#    "aud" claim is not our resource URI is rejected, even if it is otherwise
#    perfectly valid and signed by a server we trust.
verifier = JWTVerifier(
    public_key=SECRET_KEY,          # HS256 shared secret (lab only)
    algorithm=ALGORITHM,
    issuer=ISSUER,
    audience=RESOURCE,
    required_scopes=["calc:add"],
)

# 3) RemoteAuthProvider publishes RFC 9728 Protected Resource Metadata at
#    /.well-known/oauth-protected-resource/mcp, pointing clients at the
#    authorization server. This is the discovery step a 2026-07-28 client
#    performs after it receives a 401.
auth = RemoteAuthProvider(
    token_verifier=verifier,
    authorization_servers=[AnyHttpUrl(ISSUER)],
    base_url=BASE_URL,
    resource_name="MCP Lab Secure Calculator",
)

mcp = FastMCP("Secure Calc", auth=auth)


# 4) The tool itself is unremarkable. That is the point: authorization is a
#    transport/protocol concern, handled before your code ever runs.
@mcp.tool
def add(a: int, b: int) -> int:
    """Securely add two numbers. Requires the calc:add scope."""
    return a + b


if __name__ == "__main__":
    # 5) http_app() builds the Starlette app including the well-known
    #    discovery routes contributed by the auth provider.
    app = mcp.http_app(path="/mcp")
    uvicorn.run(app, host="0.0.0.0", port=8000)
