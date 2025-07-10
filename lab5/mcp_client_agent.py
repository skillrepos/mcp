# client8.py – Final fully working version for FastMCP 2.10.4 and Ollama
import asyncio
import httpx
import json
from fastmcp import Client

SERVER_URL = "http://127.0.0.1:8000/mcp/"
OLLAMA_URL = "http://127.0.0.1:11434/api/chat"

async def call_ollama(system_prompt, user_input, model_name):
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_input}
    ]

    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False
    }

    async with httpx.AsyncClient(timeout=60) as client:
        response = await client.post(OLLAMA_URL, json=payload)
        response.raise_for_status()
        result = response.json()

    return (
        result.get("message", {}).get("content")
        or result.get("response")
        or str(result)
    ).strip()

async def main():
    async with Client(SERVER_URL) as client:
        print("Connected to MCP server.")

        tools = await client.list_tools()
        tool_names = [t.name for t in tools]
        print("Available tools:", ", ".join(tool_names), "\n")

        # Get model name from server resource and parse JSON
        model_res = await client.read_resource("resource://model")
        model_json = json.loads(model_res[0].text)
        model_name_raw = model_json["model"]
        model_name = model_name_raw.split(":")[0]  # Normalize for Ollama

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
                prompt_result = await client.get_prompt(cmd)

                # Extract the first user message's content
                user_msg_template = ""
                for msg in prompt_result.messages:
                    if msg.role == "user":
                        user_msg_template = msg.content.text
                        break

                # Fill in the user input
                rendered_prompt = user_msg_template.format(text=user_input)

                # Call Ollama with the filled prompt
                result = await call_ollama(rendered_prompt, user_input, model_name)
                print(f"\n[{cmd.upper()} RESULT]\n{result}\n")

            except Exception as e:
                print("Unexpected error:", e)

if __name__ == "__main__":
    asyncio.run(main())
