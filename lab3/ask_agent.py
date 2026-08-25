# ask_agent.py - the Lab 1 agent, pointed at the help desk.
#
# Same loop you built in Lab 1: discover tools, translate them for the model,
# let the model choose, run what it chose, feed the result back. Nothing here
# is new. It ships complete so this lab can stay on the tool definitions.
#
#   python ask_agent.py                 ask the default question
#   python ask_agent.py "your question"

import asyncio
import json
import sys

import httpx

from fastmcp import Client

MCP_URL = "http://127.0.0.1:8000/mcp"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2"
MAX_TURNS = 6

QUESTION = "What is the status of order A-1043?"

SYSTEM = (
    "You are a support desk assistant. Answer the user's question using the "
    "tools you are given. Keep the final answer to one short sentence."
)

BLUE, GREEN, YELLOW, RESET = "\033[94m", "\033[92m", "\033[93m", "\033[0m"
TIMEOUT = httpx.Timeout(connect=30.0, read=300.0, write=30.0, pool=30.0)


def to_ollama_tools(mcp_tools):
    """The M x N adapter from Lab 1: MCP tool defs -> the model's format."""
    return [
        {
            "type": "function",
            "function": {
                "name": t.name,
                "description": t.description or "",
                "parameters": t.input_schema,
            },
        }
        for t in mcp_tools
    ]


async def ask_model(http, messages, tools):
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": tools,
        "stream": False,
        "keep_alive": -1,
        "options": {"num_predict": 512, "temperature": 0},
    }
    resp = await http.post(OLLAMA_URL, json=payload)
    resp.raise_for_status()
    return resp.json()["message"]


async def main():
    question = sys.argv[1] if len(sys.argv) > 1 else QUESTION

    async with Client(MCP_URL) as mcp, httpx.AsyncClient(timeout=TIMEOUT) as http:
        tools = to_ollama_tools(await mcp.list_tools())
        print(f"{BLUE}Tools offered to the model: "
              f"{', '.join(t['function']['name'] for t in tools)}{RESET}\n")

        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": question},
        ]

        for _ in range(MAX_TURNS):
            msg = await ask_model(http, messages, tools)
            messages.append(msg)

            calls = msg.get("tool_calls") or []
            if not calls:
                break

            for call in calls:
                name = call["function"]["name"]
                args = call["function"].get("arguments") or {}
                print(f"{YELLOW}-> the model chose {name}({json.dumps(args)}){RESET}")
                try:
                    result = await mcp.call_tool(name, args)
                    content = str(result.content[0].text)
                except Exception as exc:                      # unknown tool, bad args
                    content = f"error: {exc}"
                print(f"   returned: {content}")
                messages.append({"role": "tool", "tool_name": name, "content": content})

        final = next(
            (m["content"] for m in reversed(messages)
             if m.get("role") == "assistant" and (m.get("content") or "").strip()),
            "(no answer)",
        )
        print(f"\n{GREEN}ANSWER:{RESET} {final.strip()}")


if __name__ == "__main__":
    asyncio.run(main())
