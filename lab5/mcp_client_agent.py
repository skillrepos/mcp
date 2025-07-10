# mcp_client_agent.py – version for FastMCP 2.10.4 and Ollama
import asyncio
import httpx
import json
from fastmcp import Client

# ANSI color codes for terminal output
BLUE = "\033[94m"     # Bright blue for requests
GREEN = "\033[92m"    # Bright green for responses
RESET = "\033[0m"     # Reset color

# MCP server endpoint
SERVER_URL = "http://127.0.0.1:8000/mcp/"

# Ollama chat endpoint
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
    # Create an async MCP client context
    async with Client(SERVER_URL) as client:
        print(f"{GREEN}Connected to MCP server.{RESET}")

        print(f"{BLUE}Available tools: {', '.join(tool_names)}{RESET}\n")

        # Request model resource from server

        print(f"{BLUE}Model name returned from server: {model_name_raw!r}{RESET}")
        print(f"{BLUE}Model name used for Ollama: {model_name!r}{RESET}")

        while True:
            cmd = input("\nEnter tool name (or 'exit'): ").strip().lower()
            if cmd == "exit":
                break

            if cmd not in tool_names:
                print("Unknown tool:", cmd)
                continue

            user_input = input("Enter input text: ").strip()
            if not user_input:
                continue

            try:
                # Get the prompt template for this tool from the server
                print(f"{BLUE}Requesting prompt for tool: {cmd}{RESET}")

                # Extract user role template from the prompt
                user_msg_template = ""
                for msg in prompt_result.messages:
                    if msg.role == "user":
                        user_msg_template = msg.content.text
                        break

                # Fill in user input to generate final prompt

                # Send the prompt and input to the Ollama model
                # Display result in green
                print(f"\n{GREEN}[{cmd.upper()} RESULT]\n{result}{RESET}\n")

            except Exception as e:
                print("Unexpected error:", e)

if __name__ == "__main__":
    asyncio.run(main())
