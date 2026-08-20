"""
agent_mcp.py - a minimal MCP agent, no agent framework involved.

An "agent" is just this loop:
  1. tools/list  -> ask the MCP server what it can do
  2. translate the MCP tool schemas into the LLM's tool-calling format
  3. send the question + tool list to the model
  4. the model answers with tool calls -> run them via tools/call
  5. feed results back and repeat until the model answers in plain text

The HTTP plumbing and trace printing live in agent_helpers.py, so everything
below is MCP.
"""

import asyncio
import json

import httpx

from fastmcp import Client

from agent_helpers import (
    BLUE, GREEN, RESET, TIMEOUT, YELLOW,
    ask_model, print_trace, resolve_placeholders, to_number,
)

MCP_URL = "http://127.0.0.1:8931/mcp"

MAX_TURNS = 8  # stops a confused model from looping forever

SYSTEM = (
    "You are a careful calculator assistant. Use the provided tools for every "
    "arithmetic step. Do exactly one operation per tool call and never nest "
    "calls. When a step depends on an earlier tool result, pass the actual "
    "number that tool returned - never the word 'result' or any placeholder. "
    "After you have the final number, state it in one short sentence."
)


# TODO: to_ollama_tools() - translate MCP tool definitions (name, description,
#       input_schema) into the tool format the model API expects


async def main():
    async with Client(MCP_URL) as mcp, httpx.AsyncClient(timeout=TIMEOUT) as http:
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
