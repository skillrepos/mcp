import asyncio, re
from langchain_ollama import ChatOllama
from langgraph.prebuilt import create_react_agent
from langchain_mcp_adapters.client import MultiServerMCPClient

async def main():
    # Initialize the client with server configuration
    client = MultiServerMCPClient({
        "MathServer": {
            "url": "http://127.0.0.1:8931/sse",
            "transport": "sse"
        }
    })

    tools = await client.get_tools()
    print("Discovered tools:", [t.name for t in tools])

    # Create the Ollama LLM instance
    llm = ChatOllama(model="llama3.2")

    # Create the agent using 'model' as the argument, not 'llm'
    agent = create_react_agent(
        model=llm,  # or model="ollama/llama3.2" if supported by your LangGraph version
        tools=tools,
        prompt="You are a math assistant using MCP tools"
    )

    # Invoke the agent
    response = await agent.ainvoke({
        "messages": [{
            "role": "user",
            "content": "What’s 12×8 plus √144?"
        }]
    })
    # Parse out some meta characters from the LLM output
    clean_content = re.sub(r"\$\\boxed\{(.*?)\}", r"\1", response['messages'][-1].content)
    print("LLM answer :", clean_content)  

if __name__ == "__main__":
    asyncio.run(main())


