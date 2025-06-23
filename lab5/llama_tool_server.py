# llama_tool_server.py  – MCP v6-18 style 

import httpx
import uvicorn
from fastmcp import FastMCP

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL     = "llama3.2:latest"

mcp = FastMCP("LLama Summarizer")
app = mcp.http_app(path="/mcp", transport="streamable-http")

@mcp.tool(name="summarize",
          description="Summarize English text in one sentence")
async def summarize(text: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": "You summarize text."},
            {"role": "user",   "content": f"Summarize:\n{text}"}
        ],
        "stream": False
    }

    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(OLLAMA_URL, json=payload)
        r.raise_for_status()
        data = r.json()

    # Helper to normalize a “content” field that might be str | dict | list
    def extract_text(content):
        # If it’s a plain string
        if isinstance(content, str):
            return content.strip()

        # If it’s a dict with a “text” key
        if isinstance(content, dict) and "text" in content:
            return content["text"].strip()

        # If it’s a list/tuple of items (either dicts or custom objects)
        if isinstance(content, (list, tuple)) and content:
            texts = []
            for item in content:
                if isinstance(item, dict) and "text" in item:
                    texts.append(item["text"])
                else:
                    # fall back to getattr or str()
                    texts.append(getattr(item, "text", str(item)))
            return "\n".join(t.strip() for t in texts)

        # Fallback
        return str(content)

    # Ollama v2-style “results”
    if "results" in data and data["results"]:
        return extract_text(data["results"][0].get("message", {}).get("content", ""))

    # Ollama v1-style top-level “message”
    if "message" in data and isinstance(data["message"], dict):
        return extract_text(data["message"].get("content", ""))

    # Fallback: show raw JSON so you can adapt further
    return f"(unexpected format) {data}"

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
