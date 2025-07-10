# mcp_server.py – FastMCP 2.10.4-compatible server
from mcp.server.fastmcp import FastMCP

server = FastMCP(service_name="LLamaTools")

# ───────────────────────────────────────────────
# Prompt handlers – return single message
# ───────────────────────────────────────────────

@server.prompt("summarize", "You are a helpful assistant. Summarize the following text in one sentence.")
def prompt_summarize(**context):
    return {
        "role": "user",
        "content": (
            "You are a helpful assistant. Summarize the following text in one sentence.\n\n"
            f"{context.get('text', '')}"
        )
    }

@server.prompt("reword", "You are a helpful assistant. Reword the following text using clearer and simpler language.")
def prompt_reword(**context):
    return {
        "role": "user",
        "content": (
            "You are a helpful assistant. Reword the following text using clearer and simpler language.\n\n"
            f"{context.get('text', '')}"
        )
    }

@server.prompt("expand", "You are a helpful assistant. Expand on the following idea with additional detail and explanation.")
def prompt_expand(**context):
    return {
        "role": "user",
        "content": (
            "You are a helpful assistant. Expand on the following idea with additional detail and explanation.\n\n"
            f"{context.get('text', '')}"
        )
    }

# ───────────────────────────────────────────────
# Stub tools – for visibility in Inspector
# ───────────────────────────────────────────────

@server.tool("summarize")
def summarize_tool(text: str) -> str:
    return text

@server.tool("reword")
def reword_tool(text: str) -> str:
    return text

@server.tool("expand")
def expand_tool(text: str) -> str:
    return text

# ───────────────────────────────────────────────
# Model info
# ───────────────────────────────────────────────

@server.resource("resource://model")
def model_name():
    return {"model": "llama3.2:latest"}

# ───────────────────────────────────────────────

if __name__ == "__main__":
    server.run(transport="streamable-http")
