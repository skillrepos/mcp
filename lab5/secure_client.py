# secure_client.py - FastMCP 4.x, MCP spec revision 2026-07-28
#
# Walks the discovery chain a real 2026-07-28 client walks:
#   1. Call the MCP server with no token   -> 401 + WWW-Authenticate
#   2. Read the resource_metadata URL      -> RFC 9728 Protected Resource Metadata
#   3. Read the authorization server metadata (RFC 8414)
#   4. Get a token, binding it to this resource with the RFC 8707 `resource` param
#   5. Call the tool with the token
#
# In production you would let FastMCP's built-in OAuth client handle all of this
# (Client(url, auth="oauth")). We do it by hand here so you can see each hop.

import asyncio
import json

import httpx

from fastmcp import Client

MCP_ENDPOINT = "http://127.0.0.1:8000/mcp"   # canonical: no trailing slash


async def main() -> None:
    async with httpx.AsyncClient() as http:
        # --- Step 1: unauthenticated request, expect a 401 challenge ---------
        # The spec requires the 401 to name where the metadata lives.
        probe = await http.post(
            MCP_ENDPOINT,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
                "MCP-Protocol-Version": "2026-07-28",
                "Mcp-Method": "tools/list",
            },
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {
                    "_meta": {
                        "io.modelcontextprotocol/protocolVersion": "2026-07-28",
                        "io.modelcontextprotocol/clientCapabilities": {},
                    }
                },
            },
        )
        print(f"[1] Unauthenticated request -> HTTP {probe.status_code}")
        challenge = probe.headers.get("www-authenticate", "")
        print(f"    WWW-Authenticate: {challenge}")

        # Pull resource_metadata="..." out of the challenge.
        prm_url = ""
        for part in challenge.split(","):
            part = part.strip()
            if part.startswith("resource_metadata="):
                prm_url = part.split("=", 1)[1].strip('"')

        # --- Step 2: RFC 9728 Protected Resource Metadata -------------------
        prm = (await http.get(prm_url)).json()
        print(f"\n[2] Protected Resource Metadata ({prm_url}):")
        print("   ", json.dumps(prm, indent=2).replace("\n", "\n    "))

        # The metadata tells us which authorization server(s) to trust.
        as_issuer = str(prm["authorization_servers"][0]).rstrip("/")

        # --- Step 3: RFC 8414 Authorization Server Metadata -----------------
        as_meta = (
            await http.get(f"{as_issuer}/.well-known/oauth-authorization-server")
        ).json()
        print(f"\n[3] Authorization Server Metadata ({as_issuer}):")
        print(f"    issuer                  = {as_meta['issuer']}")
        print(f"    token_endpoint          = {as_meta['token_endpoint']}")
        print(f"    PKCE methods            = {as_meta['code_challenge_methods_supported']}")
        print(f"    iss param supported     = "
              f"{as_meta['authorization_response_iss_parameter_supported']}  (RFC 9207)")
        print(f"    CIMD supported          = "
              f"{as_meta['client_id_metadata_document_supported']}")

        # A real client MUST verify the returned issuer matches the URL it used.
        assert as_meta["issuer"] == as_issuer, "Issuer mismatch - possible mix-up attack"

        # --- Step 4: get a token, audience-bound to THIS resource ------------
        # `resource` is the RFC 8707 Resource Indicator. Without it, the token
        # would not be bound to this server and the server would reject it.
        token_resp = await http.post(
            as_meta["token_endpoint"],
            params={"resource": prm["resource"]},
            data={
                "username": "demo-client",
                "password": "demopass",
                "scope": "calc:add",
            },
        )
        token_resp.raise_for_status()
        token = token_resp.json()["access_token"]
        print(f"\n[4] Got token bound to audience: {prm['resource']}")

        # --- Step 5: call the tool with the token ---------------------------
        async with Client(MCP_ENDPOINT, auth=token) as c:
            print(f"\n[5] Connected. Negotiated protocol: {c.protocol_version}")
            tools = await c.list_tools()
            print("    Available tools:", [t.name for t in tools])

            result = await c.call_tool("add", {"a": 7, "b": 5})
            # FastMCP 4 returns a CallToolResult, not a bare list.
            print("    7 + 5 =", result.data)


if __name__ == "__main__":
    asyncio.run(main())
