"""
agent_helpers.py - plumbing for the lab 1 agent.

Nothing in here is MCP. It is the ordinary scaffolding any script needs:
talking to a local model over HTTP, printing a readable trace, and coping
with a small model's occasional sloppiness. It ships complete so that
agent_mcp.py can stay focused on the MCP loop itself.
"""

import asyncio
import re

import httpx

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2"

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

TIMEOUT = httpx.Timeout(connect=30.0, read=300.0, write=30.0, pool=30.0)

_NUMBER = re.compile(r"-?\d+(?:\.\d+)?")

# "...is NaN" still contains digits earlier in the sentence, so spot the
# failure word before going looking for a number.
_NOT_A_NUMBER = re.compile(r"\b(nan|undefined|infinity|error)\b", re.IGNORECASE)


async def ask_model(client, messages, tools):
    """One turn with the LLM. Retries because cold local models are slow."""
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False,
        # Ollama unloads an idle model after 5 minutes by default, and this
        # loop makes several calls with a human typing in between. Reloading
        # a 3B model on a 4-core box costs far more than the answer does.
        "keep_alive": -1,
        # A small model will happily ramble. The answer we want is one line.
        "options": {"num_predict": 512},
    }
    for attempt in range(4):
        try:
            resp = await client.post(OLLAMA_URL, json=payload)
            resp.raise_for_status()
            return resp.json()["message"]
        except (httpx.TimeoutException, httpx.ConnectError):
            if attempt == 3:
                raise
            await asyncio.sleep(1.5 * (attempt + 1))
    raise RuntimeError("model unreachable")


def _is_number(value) -> bool:
    """True only if this value IS a number - no guessing, no extraction."""
    try:
        float(str(value).strip())
        return True
    except (TypeError, ValueError):
        return False


def resolve_placeholders(args, last_value):
    """Repair arguments the model sent as text instead of numbers.

    The tool's JSON Schema says these parameters are numbers. A small model
    will sometimes send a stand-in meaning "the number from the last call"
    instead - "result", "<result>", "${result}", "previous answer". Rather
    than trying to list every spelling it might invent, we test the only
    thing that actually matters: is this a number? If it is not, and we have
    a real number from the previous call, that is what it meant.
    """
    if last_value is None:
        return args
    return {
        k: (v if _is_number(v) else last_value)
        for k, v in args.items()
    }


def to_number(value, fallback=None):
    """Best-effort numeric read of a tool result.

    A server may answer with a bare number or with a sentence like
    "The product of 12 and 8 is 96". Take the last number either way, and
    keep the previous value if there isn't a usable one. This is the opposite
    job from _is_number: here we are reading a RESULT, so prose is expected.
    """
    if isinstance(value, bool) or value is None:
        return fallback
    if isinstance(value, (int, float)):
        n = float(value)
    else:
        text = str(value)
        if _NOT_A_NUMBER.search(text):
            return fallback
        found = _NUMBER.findall(text)
        if not found:
            return fallback
        n = float(found[-1])
    if n != n or n in (float("inf"), float("-inf")):  # NaN or infinity
        return fallback
    return int(n) if n.is_integer() else n


def print_trace(messages):
    """Print the conversation, then the model's final plain-text answer."""
    print(f"\n{BLUE}=== FULL AGENT TRACE ==={RESET}")
    for m in messages:
        role = m.get("role")
        if role == "system":
            continue
        if role == "tool":
            print(f"TOOL RESULT ({m.get('tool_name')}): {m.get('content')}")
        elif m.get("tool_calls"):
            names = [c["function"]["name"] for c in m["tool_calls"]]
            print(f"ASSISTANT: (requested tools: {', '.join(names)})")
        elif m.get("content"):
            print(f"{role.upper()}: {m['content']}")

    final = ""
    for m in reversed(messages):
        if m.get("role") == "assistant" and (m.get("content") or "").strip():
            final = m["content"].strip()
            break

    print(f"\n{GREEN}=== FINAL ANSWER ==={RESET}")
    print(final)
