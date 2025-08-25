# mcp_server.py – FastMCP 2.10.4-compatible server
from mcp.server.fastmcp import FastMCP

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
RESET = "\033[0m"

# Create a FastMCP server instance with a service name
server = FastMCP()

# ───────────────────────────────────────────────
# Prompt handlers – return single message templates
# These are used by clients to fetch structured prompts
# ───────────────────────────────────────────────

@server.prompt("summarize", "You are a helpful assistant. Summarize the following text in one sentence.")
def prompt_summarize(**context):

@server.prompt("reword", "You are a helpful assistant. Reword the following text using clearer and simpler language.")
def prompt_reword(**context):

@server.prompt("expand", "You are a helpful assistant. Expand on the following idea with additional detail and explanation.")
def prompt_expand(**context):

# ───────────────────────────────────────────────
# Tool handlers – used to expose tool names to the client
# These stubs are for visibility only; they do not perform actions
# ───────────────────────────────────────────────


# ───────────────────────────────────────────────
# Resource endpoint – used to expose model metadata
# ───────────────────────────────────────────────

@server.resource("resource://model")

# ───────────────────────────────────────────────
# Entry point – start the FastMCP server with streamable HTTP
# ───────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{BLUE}Starting FastMCP server on streamable HTTP...{RESET}")
    server.run(transport="streamable-http")
