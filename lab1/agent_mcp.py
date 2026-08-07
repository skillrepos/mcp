"""
agent_mcp.py - a minimal MCP agent, no agent framework involved.

Updated 2026-08-03 for MCP specification revision 2026-07-28.

An "agent" is just this loop:
  1. tools/list  -> ask the MCP server what it can do
  2. translate the MCP tool schemas into the LLM's tool-calling format
  3. send the question + tool list to the model
  4. the model answers with tool calls -> run them via tools/call
  5. feed results back and repeat until the model answers in plain text

Merge in the completed code to fill the TODOs below.
"""

import asyncio
import json

import httpx

from fastmcp import Client

MCP_URL = "http://127.0.0.1:8931/mcp"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL = "llama3.2"

BLUE = "\033[94m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
RESET = "\033[0m"

SYSTEM = (
    "You are a careful calculator assistant. Use the provided tools for every "
    "arithmetic step. Do exactly one operation per tool call and never nest "
    "calls. After you have the final number, state it in one short sentence."
)


# TODO: to_ollama_tools() - translate MCP tool definitions (name, description,
#       input_schema) into the tool format the model API expects


async def ask_model(client: httpx.AsyncClient, messages, tools):
    """One turn with the LLM. Retries because cold local models are slow."""
    payload = {"model": MODEL, "messages": messages, "tools": tools, "stream": False}
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


async def main():
    timeout = httpx.Timeout(connect=30.0, read=300.0, write=30.0, pool=30.0)

    async with Client(MCP_URL) as mcp, httpx.AsyncClient(timeout=timeout) as http:
        print(f"{BLUE}Connected using protocol {mcp.protocol_version}{RESET}")

        # TODO: discovery - call list_tools() and convert them for the model

        messages = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": "What is 12 x 8 / 3 ?"},
        ]

        # TODO: the agent loop - ask the model, run any tool calls it makes
        #       via mcp.call_tool(), append the results, and repeat until the
        #       model replies with plain text

        # TODO: print the full trace and the final natural-language answer


if __name__ == "__main__":
    asyncio.run(main())
