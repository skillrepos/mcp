# mcp_client_agent.py – Final fully working version for FastMCP 2.10.4 and Ollama
import asyncio
import httpx
import json
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8000/mcp/"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

async def call_ollama(system_prompt, user_input, model_name):

    }

    async with httpx.AsyncClient(timeout=60) as client:

    return (
        result.get("message", {}).get("content")
        or result.get("response")
        or str(result)
    ).strip()

async def main():
    async with Client(SERVER_URL) as client:
        print("Connected to MCP server.")

        print("Available tools:", ", ".join(tool_names), "\n")

        # Get model name from server resource and parse JSON

        print("Model name returned from server:", repr(model_name_raw))
        print("Model name used for Ollama:", repr(model_name))

        while True:
            cmd = input("Enter tool name (or 'exit'): ").strip().lower()
            if cmd == "exit":
                break

            if cmd not in tool_names:
                print("Unknown tool:", cmd)
                continue

            user_input = input("Enter input text: ").strip()
            if not user_input:
                continue

            try:
                # Get the prompt from the server

                # Extract the first user message's content
                user_msg_template = ""
                for msg in prompt_result.messages:
                    if msg.role == "user":
                        user_msg_template = msg.content.text
                        break

                # Fill in the user input

                # Call Ollama with the filled prompt

            except Exception as e:
                print("Unexpected error:", e)

if __name__ == "__main__":
    asyncio.run(main())
