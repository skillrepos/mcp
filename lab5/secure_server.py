# secure_server.py - FastMCP 4.x, MCP spec revision 2026-07-28
#
# A single "add" tool protected by OAuth 2.1 bearer tokens.
#
# The MCP server is an OAuth RESOURCE SERVER. It never issues a token; it only
# checks the one presented on each request, in this order, before your tool
# code runs:
#
#   signature   was it really minted by the key we share with the issuer?
#   issuer      does `iss` name an authorization server we trust?
#   audience    does `aud` name THIS server? (RFC 8707 - a MUST)
#   expiry      is `exp` still in the future?
#   scope       does `scope` include what this tool needs?
#
# The first four failing gives 401 invalid_token - the request is not
# authenticated. Scope failing gives 403 insufficient_scope - authenticated,
# but not authorized to do this.
#
# There is no session to protect - 2026-07-28 removed Mcp-Session-Id - so
# every request is authorized on its own, from its own Authorization header.

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

# 2) The token verifier: signature, issuer, audience and expiry. `audience`
#    is what enforces RFC 8707 - a token whose "aud" is not our resource URI
#    is rejected even if it is otherwise valid and signed by a key we trust.
verifier = JWTVerifier(
    public_key=SECRET_KEY,          # HS256 shared secret (lab only)
    algorithm=ALGORITHM,
    issuer=ISSUER,
    audience=RESOURCE,
)

# 3) RemoteAuthProvider wraps the verifier and publishes RFC 9728 Protected
#    Resource Metadata at /.well-known/oauth-protected-resource/mcp, which is
#    how a client that only knows our URL finds the authorization server.
#    challenge_scopes is what the 401 advertises in WWW-Authenticate.
auth = RemoteAuthProvider(
    token_verifier=verifier,
    authorization_servers=[AnyHttpUrl(ISSUER)],
    base_url=BASE_URL,
    resource_name="MCP Lab Secure Calculator",
    challenge_scopes=["calc:add"],
)

# 4) Scope is enforced at the endpoint, AFTER the token itself has been
#    accepted. That is what makes a valid token without calc:add a 403
#    (insufficient_scope) rather than a 401: we know who you are, you just
#    can't do this.
auth.required_scopes = ["calc:add"]

mcp = FastMCP("Secure Calc", auth=auth)


# 5) The tool itself is unremarkable. That is the point: authorization is a
#    transport/protocol concern, handled before your code ever runs.
@mcp.tool
def add(a: int, b: int) -> int:
    """Securely add two numbers. Requires the calc:add scope."""
    return a + b


if __name__ == "__main__":
    # 6) http_app() builds the Starlette app including the well-known
    #    discovery routes contributed by the auth provider.
    app = mcp.http_app(path="/mcp")
    uvicorn.run(app, host="0.0.0.0", port=8000)
