import asyncio, re
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Utility: Format tool call arguments for display
def format_args(args: dict) -> str:
    """
    Pretty-print tool arguments for logging.
    If args are quoted numbers (e.g., "12"), this will coerce them for display.
    This does NOT affect what gets sent to the server.
    """
    clean_args = {}
    for k, v in args.items():
        if isinstance(v, str) and v.isdigit():
            clean_args[k] = int(v)
        else:
            clean_args[k] = v
    return str(clean_args)

async def main():
    # ─────────────────────────────────────────────────────────────────────────────
    # 1. Connect to the MCP server running on localhost (assumed port 8931)
    # ─────────────────────────────────────────────────────────────────────────────
    client = MultiServerMCPClient({
        "CalcMCP": {
            "url": "http://127.0.0.1:8931/sse",
            "transport": "sse"
        }
    })

    # 2. Dynamically discover all tools advertised by the MCP server
    tools = await client.get_tools()
    print("Discovered tools:", [t.name for t in tools])

    # 3. Create a bullet list of tools for use in the agent's system prompt
    tool_list = "\n".join(f"- {t.name}: {t.description}" for t in tools)

    # 4. Create a local LLM instance (Ollama) for use in the agent
    llm = ChatOllama(model="llama3.2")

    # ─────────────────────────────────────────────────────────────────────────────
    # 5. Create the ReAct-style agent using LangGraph + MCP tools + LLM
    #    Prompt clearly forbids math reasoning and tool nesting.
    # ─────────────────────────────────────────────────────────────────────────────
    agent = create_react_agent(
        model=llm,
        tools=tools,
        prompt=(
            "You are a math assistant.\n"
            "You may not do math yourself — all calculations must use tools.\n"
            "You must follow these rules strictly:\n"
            "- Use only one tool at a time.\n"
            "- Never call a tool using another tool as an argument.\n"
            "- Always wait for a result before using its output in another tool.\n"
            "- Use numeric values directly — do NOT quote numbers (write 12 not \"12\").\n"
            "- Quoted numbers or nested calls will cause errors or wrong answers.\n\n"
            "Here are the available tools:\n"
            f"{tool_list}\n\n"
            "Begin by responding to the user query using tool calls only."
        )
    )

    # 6. Set the user prompt to a math expression involving multiple operations
    user_prompt = "What’s 12×8 / 3 ?"

    # ─────────────────────────────────────────────────────────────────────────────
    # 7. Invoke the agent with the user prompt
    #    The agent will reason through which tools to use step-by-step
    # ─────────────────────────────────────────────────────────────────────────────
    response = await agent.ainvoke({
        "messages": [HumanMessage(content=user_prompt)]
    })

    # ─────────────────────────────────────────────────────────────────────────────
    # 8. Print the full trace of reasoning: tool calls, results, and final message
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n=== FULL AGENT TRACE ===")
    for msg in response['messages']:
        if isinstance(msg, HumanMessage):
            print("USER:", msg.content)

        elif isinstance(msg, AIMessage):
            print("ASSISTANT (LLM):", msg.content)
            if msg.tool_calls:
                for call in msg.tool_calls:
                    tool = call.get("name")
                    args = call.get("args", {})
                    print(f"→ TOOL CALL: {tool}({format_args(args)})")

        elif isinstance(msg, ToolMessage):
            print(f"← TOOL RESULT for ID {msg.tool_call_id}:", msg.content)

        else:
            print(f"{type(msg).__name__}:", msg)

    # ─────────────────────────────────────────────────────────────────────────────
    # 9. Clean and print the final assistant message
    # ─────────────────────────────────────────────────────────────────────────────
    print("\n=== FINAL NATURAL LANGUAGE ANSWER ===")
    final = response['messages'][-1]
    content = getattr(final, "content", "")
    clean_content = re.sub(r"\$\\boxed\{(.*?)\}", r"\1", content)
    print(clean_content)

if __name__ == "__main__":
    asyncio.run(main())
