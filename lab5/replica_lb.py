# replica_lb.py - a deliberately tiny round-robin load balancer for the lab.
#
# This is the whole point of the 2026-07-28 stateless redesign: the thing in
# front of your MCP replicas can be THIS dumb. No session table, no cookie
# parsing, no JSON inspection - it forwards each request to the next backend
# in rotation and prints which replica got it.
#
# Usage:  python replica_lb.py [port] [backend...]
# Default: listen on 8000, round-robin to http://127.0.0.1:8001 and :8002

import itertools
import sys

from aiohttp import ClientSession, web

LISTEN = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
BACKENDS = sys.argv[2:] or ["http://127.0.0.1:8001", "http://127.0.0.1:8002"]
rr = itertools.cycle(BACKENDS)

CYAN, YELLOW, RESET = "\033[96m", "\033[93m", "\033[0m"

# Hop-by-hop headers must not be forwarded (RFC 9110 §7.6.1).
HOP = {"connection", "keep-alive", "transfer-encoding", "te", "upgrade",
       "proxy-authenticate", "proxy-authorization", "host", "content-length"}


async def proxy(request: web.Request) -> web.Response:
    backend = next(rr)
    body = await request.read()

    # The ONE piece of MCP awareness here is optional and read-only: we log
    # the Mcp-Method / Mcp-Name headers to show what header-based routing
    # would see - without ever parsing the JSON body.
    method = request.headers.get("Mcp-Method", "-")
    name = request.headers.get("Mcp-Name", "")
    print(f"{CYAN}[lb] {request.method} {request.path}  "
          f"Mcp-Method={method}{' Mcp-Name=' + name if name else ''}  "
          f"->  {YELLOW}{backend}{RESET}")

    headers = {k: v for k, v in request.headers.items() if k.lower() not in HOP}
    async with ClientSession() as s:
        async with s.request(request.method, backend + request.path_qs,
                             data=body, headers=headers) as resp:
            payload = await resp.read()
            out = {k: v for k, v in resp.headers.items() if k.lower() not in HOP}
            return web.Response(status=resp.status, body=payload, headers=out)


app = web.Application()
app.router.add_route("*", "/{tail:.*}", proxy)

if __name__ == "__main__":
    print(f"{CYAN}[lb] round-robin on http://127.0.0.1:{LISTEN}  ->  "
          f"{', '.join(BACKENDS)}{RESET}")
    web.run_app(app, host="127.0.0.1", port=LISTEN, print=None)
