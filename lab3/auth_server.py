# auth_server.py
#
# A miniature OAuth 2.1-style authorization server for the lab.
# Updated 2026-08-03 for MCP spec revision 2026-07-28.
#
# What changed for the 2026-07-28 spec:
#   * Tokens now carry an "aud" (audience) equal to the MCP server's CANONICAL
#     RESOURCE URI, per RFC 8707 Resource Indicators. The MCP server MUST reject
#     any token that is not audience-bound to itself.
#   * We publish RFC 8414 authorization-server metadata at
#     /.well-known/oauth-authorization-server so the MCP client can discover us.
#   * The metadata advertises `authorization_response_iss_parameter_supported`,
#     the RFC 9207 issuer-identification signal that 2026-07-28 clients use to
#     defend against authorization-server mix-up attacks.
#   * The metadata advertises `client_id_metadata_document_supported`, since
#     2026-07-28 deprecates Dynamic Client Registration in favor of CIMD.
#
# NOTE: This is a teaching stand-in, not a production authorization server.
# It uses a symmetric HS256 key shared with the MCP server so the lab can run
# entirely offline. Real deployments use asymmetric keys published via JWKS.

from datetime import datetime, timedelta, timezone

import uvicorn
from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import JWTError, jwt

SECRET_KEY = "mcp-lab-secret"                       # shared with the MCP server
ALGORITHM = "HS256"
ISSUER = "http://127.0.0.1:9000"                    # this server's issuer identity

# 1) AUDIENCE is now the MCP server's canonical resource URI, not a made-up
#    label. RFC 8707 canonical form: lowercase scheme/host, no fragment.
RESOURCE = "http://127.0.0.1:8000/mcp"

EXPIRES_IN = 3600

# Fake "client registry" so we don't need users or a database.
_fake_clients = {
    "demo-client": {
        "client_secret": "demopass",
        "scopes": ["calc:add"],
    }
}

app = FastAPI(title="MCP Lab - Authorization Server")


def _create_access_token(sub: str, scopes: list[str], audience: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "scope": " ".join(scopes),
        "aud": audience,      # 2) audience binding - the heart of RFC 8707
        "iss": ISSUER,        # 3) issuer - the MCP server verifies this too
        "iat": now,
        "exp": now + timedelta(seconds=EXPIRES_IN),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 4) RFC 8414 authorization server metadata.
#    A 2026-07-28 MCP client walks: 401 -> protected resource metadata ->
#    THIS document -> authorization/token endpoints.
@app.get("/.well-known/oauth-authorization-server")
def as_metadata():
    return {
        "issuer": ISSUER,
        "token_endpoint": f"{ISSUER}/token",
        "introspection_endpoint": f"{ISSUER}/introspect",
        "grant_types_supported": ["client_credentials", "authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        # PKCE: clients MUST verify S256 is offered or refuse to proceed.
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["calc:add"],
        # RFC 9207 - new emphasis in 2026-07-28. Clients compare the `iss`
        # returned on the authorization response against this issuer before
        # redeeming an authorization code.
        "authorization_response_iss_parameter_supported": True,
        # 2026-07-28 deprecates Dynamic Client Registration in favor of
        # Client ID Metadata Documents. Advertising this tells clients to
        # prefer a URL-form client_id over calling /register.
        "client_id_metadata_document_supported": True,
    }


@app.post("/token")
def token(form: OAuth2PasswordRequestForm = Depends(), resource: str | None = None):
    """
    Simplified grant: client_id + secret -> {access_token, expires_in}.

    5) `resource` is the RFC 8707 Resource Indicator. A 2026-07-28 client MUST
       send it on BOTH the authorization request and the token request. We honor
       it by minting a token whose audience is that resource, so the token can
       only be spent at the MCP server it was requested for.
    """
    client = _fake_clients.get(form.username)
    if not client or client["client_secret"] != form.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    audience = resource or RESOURCE
    access_token = _create_access_token(form.username, client["scopes"], audience)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": EXPIRES_IN,
        "scope": " ".join(client["scopes"]),
    }


@app.post("/introspect")
def introspect(token: str = Body(..., embed=True)):
    """RFC 7662-style introspection, so you can inspect a token in the lab."""
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM],
            audience=RESOURCE,
            issuer=ISSUER,
        )
    except JWTError as exc:
        return {"active": False, "error": str(exc)}

    return {
        "active": True,
        "sub": payload["sub"],
        "scope": payload["scope"],
        "aud": payload["aud"],
        "iss": payload["iss"],
        "exp": payload["exp"],
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
