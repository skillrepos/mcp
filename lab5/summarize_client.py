async def main():
    # Create an asynchronous context-managed MCP client.
    # The `Client` automatically handles connecting via HTTP POST/SSE under the hood.
    async with Client("http://127.0.0.1:9000/mcp") as c:
        # The text to summarize
        text = (
            "Model-Context Protocol (MCP) lets clients discover, version "
            "and call AI tools, prompts and resources over a simple RPC/HTTP interface."
        )

        # Call the 'summarize' tool on the MCP server, passing a JSON-compatible dict
        # `call_tool` returns either a single response object or a list of streamed chunks
        result = await c.call_tool("summarize", {"text": text})

        print("Summary:")

        # Normalize to a list: handle streaming responses (list) or single result
        chunks = result if isinstance(result, list) else [result]

        # Iterate over each chunk and print its content
        for chunk in chunks:
            # Many MCP clients return objects with a `.text` attribute for actual text content.
            # Use getattr to safely retrieve `.text`, falling back to str(chunk) if not present.
            content = getattr(chunk, "text", None)
            if isinstance(content, str):
                print(content)
            else:
                # If chunk is already a simple type (e.g. str), just print it
                print(str(chunk))

# Entry point: run the `main` coroutine
if __name__ == "__main__":
    asyncio.run(main())
