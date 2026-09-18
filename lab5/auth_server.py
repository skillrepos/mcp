# auth_server.py
#
# A miniature OAuth 2.1-style authorization server for the lab.
# MCP spec revision 2026-07-28.
#
# Its one real job is to MINT TOKENS. Every token it issues is a signed JWT
# carrying five claims the MCP server will check on every request:
#
#   sub    who the token was issued to (the client id)
#   scope  what the holder may do ("calc:add")
#   aud    which server it may be spent at - the MCP server's canonical
#          resource URI, per RFC 8707. A token minted for one server is
#          useless at another.
#   iss    who minted it - this server. The MCP server only trusts tokens
#          from issuers it was configured with.
#   exp    when it stops working.
#
# It also publishes RFC 8414 metadata at /.well-known/oauth-authorization-server
# so a client that only knows the MCP server's URL can find the token endpoint
# by itself. secure_client.py shows that discovery happening.
#
# NOTE: This is a teaching stand-in, not a production authorization server.
# It uses a symmetric HS256 key shared with the MCP server so the lab can run
# entirely offline. Real deployments use asymmetric keys published via JWKS,
# and real users, not the two demo clients below.

from datetime import datetime, timedelta, timezone

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt

SECRET_KEY = "mcp-lab-secret"                       # shared with the MCP server
ALGORITHM = "HS256"
ISSUER = "http://127.0.0.1:9000"                    # this server's issuer identity

# 1) AUDIENCE is the MCP server's canonical resource URI (RFC 8707):
#    lowercase scheme and host, no trailing slash, no fragment.
RESOURCE = "http://127.0.0.1:8000/mcp"

DEFAULT_EXPIRES_IN = 3600                           # seconds

# 2) A fake "client registry" so the lab needs no users or database.
#    demo-client may add; readonly-client is a real, valid client that
#    simply was never granted calc:add.
_fake_clients = {
    "demo-client": {
        "client_secret": "demopass",
        "scopes": ["calc:add"],
    },
    "readonly-client": {
        "client_secret": "readonlypass",
        "scopes": ["calc:read"],
    },
}

app = FastAPI(title="MCP Lab - Authorization Server")


def _create_access_token(sub: str, scopes: list[str], audience: str,
                         expires_in: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "scope": " ".join(scopes),
        "aud": audience,      # 3) audience binding - the heart of RFC 8707
        "iss": ISSUER,        # 4) issuer - the MCP server verifies this too
        "iat": now,
        "exp": now + timedelta(seconds=expires_in),
    }
    # 5) Signing is what makes the claims trustworthy. Anyone can READ a JWT;
    #    only a holder of the key can MAKE one, or change one without the
    #    signature failing.
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# 6) RFC 8414 authorization server metadata. A client that received a 401
#    from the MCP server reads this to learn where the token endpoint is.
@app.get("/.well-known/oauth-authorization-server")
def as_metadata():
    return {
        "issuer": ISSUER,
        "token_endpoint": f"{ISSUER}/token",
        "grant_types_supported": ["client_credentials", "authorization_code"],
        "token_endpoint_auth_methods_supported": ["client_secret_post", "none"],
        # PKCE: clients MUST verify S256 is offered or refuse to proceed.
        "code_challenge_methods_supported": ["S256"],
        "scopes_supported": ["calc:add", "calc:read"],
        # RFC 9207 issuer identification, which clients use to defend
        # against authorization-server mix-up attacks.
        "authorization_response_iss_parameter_supported": True,
        # Client ID Metadata Documents replace Dynamic Client Registration.
        "client_id_metadata_document_supported": True,
    }


# 7) The token endpoint. Simplified grant: client id + secret in, JWT out.
#
#    `resource` is the RFC 8707 Resource Indicator: the server the client
#    intends to spend the token at. It becomes the token's audience.
#
#    `expires_in` exists only so the lab can mint a short-lived token and
#    watch it expire. A real authorization server decides lifetimes itself.
@app.post("/token")
def token(form: OAuth2PasswordRequestForm = Depends(),
          resource: str | None = None,
          expires_in: int | None = None):
    client = _fake_clients.get(form.username)
    if not client or client["client_secret"] != form.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid client credentials",
        )

    audience = resource or RESOURCE
    lifetime = min(expires_in or DEFAULT_EXPIRES_IN, DEFAULT_EXPIRES_IN)
    access_token = _create_access_token(form.username, client["scopes"],
                                        audience, lifetime)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": lifetime,
        "scope": " ".join(client["scopes"]),
    }


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
