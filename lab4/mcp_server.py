# mcp_server.py – FastMCP 3.x-compatible server
# Updated 2026-03-20: Migrated from mcp.server.fastmcp to fastmcp 3.x;
#   prompt handlers now return strings instead of dicts.
from fastmcp import FastMCP

# ANSI color codes
BLUE = "\033[94m"
GREEN = "\033[92m"
RESET = "\033[0m"

# Create a FastMCP server instance with a service name
server = FastMCP()

# ───────────────────────────────────────────────
# Prompt handlers – return string templates
# These are used by clients to fetch structured prompts
# ───────────────────────────────────────────────

@server.prompt("summarize")
def prompt_summarize(text: str) -> str:
    """You are a helpful assistant. Summarize the following text in one sentence."""

@server.prompt("reword")
def prompt_reword(text: str) -> str:
    """You are a helpful assistant. Reword the following text using clearer and simpler language."""

@server.prompt("expand")
def prompt_expand(text: str) -> str:
    """You are a helpful assistant. Expand on the following idea with additional detail and explanation."""

# ───────────────────────────────────────────────
# Tool handlers – used to expose tool names to the client
# These stubs are for visibility only; they do not perform actions
# ───────────────────────────────────────────────


# ───────────────────────────────────────────────
# Resource – lets the client discover the model to use
# ───────────────────────────────────────────────

@server.resource("resource://model")

# ───────────────────────────────────────────────
# Entry point – start the FastMCP server with streamable HTTP
# ───────────────────────────────────────────────

if __name__ == "__main__":
    print(f"{BLUE}Starting FastMCP server on streamable HTTP...{RESET}")
    server.run(transport="streamable-http")

