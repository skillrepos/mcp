# show_tools.py - print exactly what the model is told about this server.
#
# An agent never sees your source code. It sees this: a name, a description,
# and a JSON Schema, translated from tools/list into whatever format its
# model API expects. If the answer isn't in here, the model is guessing.
#
#   python show_tools.py          show the tool list
#   python show_tools.py --scan   also check the descriptions for trouble

import asyncio
import json
import re
import sys

from fastmcp import Client

URL = "http://127.0.0.1:8000/mcp"

BOLD, DIM, RED, GREEN, RESET = "\033[1m", "\033[2m", "\033[91m", "\033[92m", "\033[0m"

# A description is written for a human reading your docs. Wording that
# instructs the *model* instead does not belong there - so look for it.
SUSPICIOUS = re.compile(
    r"(ignore (the |all )?(previous|prior|above)|disregard|you must|"
    r"before (answering|responding)|always call|do not (tell|mention|reveal)|"
    r"system (prompt|notice|instruction)|important:)",
    re.IGNORECASE,
)


async def main() -> None:
    scan = "--scan" in sys.argv
    async with Client(URL) as mcp:
        tools = await mcp.list_tools()
        print(f"\n{len(tools)} tools on {URL}\n")

        for t in tools:
            print(f"{BOLD}{t.name}{RESET}")
            print(f"  description: {t.description or DIM + '(none)' + RESET}")
            print(f"  schema:      {json.dumps(t.input_schema.get('properties', {}))}")
            required = t.input_schema.get("required", [])
            print(f"  required:    {required or '(none)'}")

            if scan:
                hits = [h.group(0) for h in SUSPICIOUS.finditer(t.description or "")]
                if hits:
                    print(f"  {RED}SUSPICIOUS{RESET}  description talks to the model, "
                          f"not to you: {', '.join(repr(h) for h in hits)}")
                else:
                    print(f"  {GREEN}ok{RESET}          nothing instruction-like")
            print()


if __name__ == "__main__":
    asyncio.run(main())
