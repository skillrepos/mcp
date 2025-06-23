# llama_tool_server.py  – MCP v6-18 style with latency measurement

import time
import httpx
import uvicorn
from fastmcp import FastMCP

OLLAMA_URL = "http://127.0.0.1:11434/api/chat"
MODEL     = "llama3.2:latest"

# Create FastMCP instance
mcp = FastMCP("LLama Summarizer")

# Mount both RPC (POST) and SSE (GET) at /mcp
app = mcp.http_app(path="/mcp", transport="streamable-http")

# Healthcheck tool
@mcp.tool(name="ping", description="Check server health")
async def ping() -> str:
    return "pong"

# Summarize tool with latency measurement
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

    # Measure round‐trip time to Ollama
    start = time.time()
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(OLLAMA_URL, json=payload)
    r.raise_for_status()
    duration_ms = int((time.time() - start) * 1000)
    data = r.json()

    # Helper to normalize various content shapes
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
        summary = extract_text(data["results"][0]
                               .get("message", {})
                               .get("content", ""))
        return f"{summary}\n\n( took {duration_ms}ms)"

    # Ollama v1-style top-level “message”
    if "message" in data and isinstance(data["message"], dict):
        summary = extract_text(data["message"].get("content", ""))
        return f"{summary}\n\n( took {duration_ms}ms)"

    # Fallback
    return f"(unexpected format) {data}  (took {duration_ms}ms)"

# Run the app
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
