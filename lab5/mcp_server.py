# mcp_server.py – FastMCP 2.10.4-compatible server
from mcp.server.fastmcp import FastMCP

server = FastMCP(service_name="LLamaTools")

# ───────────────────────────────────────────────
# Prompt handlers – return single message
# ───────────────────────────────────────────────

@server.prompt("summarize", "You are a helpful assistant. Summarize the following text in one sentence.")
def prompt_summarize(**context):
    return {
    }

@server.prompt("reword", "You are a helpful assistant. Reword the following text using clearer and simpler language.")
def prompt_reword(**context):
    return {
    }

@server.prompt("expand", "You are a helpful assistant. Expand on the following idea with additional detail and explanation.")
def prompt_expand(**context):
    return {
    }

# ───────────────────────────────────────────────
# Stub tools – for visibility in Inspector
# ───────────────────────────────────────────────


# ───────────────────────────────────────────────
# Model info
# ───────────────────────────────────────────────

@server.resource("resource://model")

# ───────────────────────────────────────────────

if __name__ == "__main__":
    server.run(transport="streamable-http")
