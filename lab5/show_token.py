# show_token.py - open up a JWT and show what the MCP server will look at.
#
#   python show_token.py $TOKEN
#
# A JWT is three base64url strings joined by dots: header.payload.signature.
# The first two are NOT encrypted - anyone holding the token can read them,
# and this script does. The third is what makes them trustworthy: an HMAC
# over the first two that only a holder of the signing key can produce.
# This script does not check the signature; the secure server does.

import base64
import json
import sys
from datetime import datetime, timezone

BOLD, DIM, RESET = "\033[1m", "\033[2m", "\033[0m"

# What each claim means to the server that receives the token.
CLAIMS = {
    "sub":   "who the token was issued to",
    "scope": "what the holder may do",
    "aud":   "which server it may be spent at   (RFC 8707)",
    "iss":   "who minted it",
    "iat":   "when it was minted",
    "exp":   "when it stops working",
}


def _b64decode(part: str) -> dict:
    part += "=" * (-len(part) % 4)            # restore stripped padding
    return json.loads(base64.urlsafe_b64decode(part))


def main() -> None:
    if len(sys.argv) < 2 or not sys.argv[1]:
        sys.exit("usage: python show_token.py $TOKEN")

    token = sys.argv[1]
    try:
        header_b64, payload_b64, signature_b64 = token.split(".")
        header, payload = _b64decode(header_b64), _b64decode(payload_b64)
    except ValueError:
        sys.exit("that is not a JWT: expected three dot-separated parts")

    print(f"\n{BOLD}1. HEADER{RESET}      {DIM}{header_b64}{RESET}")
    for key, value in header.items():
        print(f"   {key:5} = {value}")

    print(f"\n{BOLD}2. PAYLOAD{RESET}     {DIM}{payload_b64[:40]}...{RESET}")
    now = datetime.now(timezone.utc)
    for key, value in payload.items():
        shown = value
        if key in ("iat", "exp") and isinstance(value, (int, float)):
            when = datetime.fromtimestamp(value, tz=timezone.utc)
            delta = int((when - now).total_seconds())
            tense = f"in {delta} s" if delta >= 0 else f"{-delta} s ago"
            shown = f"{value}  ({when:%H:%M:%S} UTC, {tense})"
        note = CLAIMS.get(key, "")
        print(f"   {key:5} = {shown:<52} {DIM}{note}{RESET}")

    print(f"\n{BOLD}3. SIGNATURE{RESET}   {DIM}{signature_b64}{RESET}")
    print("   HMAC-SHA256 over header.payload, using the issuer's key.")
    print("   Readable without the key; unforgeable without it.\n")


if __name__ == "__main__":
    main()
