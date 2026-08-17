# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 8.3 - 08/17/26 

**Versions of dialogs, buttons, etc. shown in screenshots may differ from current version used in dev environments**

**Follow the startup instructions in the README.md file IF NOT ALREADY DONE!**

**NOTES:**
1. We will be working in the public GitHub.com, not a private instance.
2. Chrome may work better than Firefox for some tasks.
3. Substitute the appropriate key combinations for your operating system where needed.
4. The default environment will be a GitHub Codespace (with everything you need already installed). If you prefer to use your own environment, you are responsible for installing the needed apps and dependencies in it. Some things in the lab may be different if you use your own environment.
5. To copy and paste in the codespace, you may need to use keyboard commands - CTRL-C and CTRL-V.**
6. VPNs may interfere with the ability to run the codespace. It is recommended to not use a VPN if you run into problems.
7. When your cursor is in a file in the editor and you need to type a command, be sure to click back in *TERMINAL* before typing so you don't write over file contents. If you do inadvertently write over contents, you can use "git checkout <filename>" to get the most recent committed version.
</br></br></br>
8. Except where a lab gives specific instructions to click on a button in a pop-up, you can close any pop-up that comes up.

</br></br>

---

## What changed in MCP specification revision 2026-07-28

**Read this before Lab 1.** These labs target the current MCP specification revision,
`2026-07-28`, which is the largest breaking change the protocol has had. If you have
used MCP before, these are the things that will surprise you:

| Gone | What replaced it |
|---|---|
| The `initialize` / `initialized` handshake | Every request carries its own protocol version and capabilities in `_meta` |
| The `Mcp-Session-Id` header | Nothing. Servers mint **explicit handles** and return them as ordinary data |
| Servers pushing requests to clients | **MRTR** - the server *responds* with `input_required` and the client retries |
| `GET` on the MCP endpoint (the SSE stream) | `subscriptions/listen`, which clients opt into explicitly |
| `ping`, `logging/setLevel`, `notifications/roots/list_changed` | Removed outright |

**Deprecated** (still functional). **Roots**, **Sampling**, **Logging** and
**Dynamic Client Registration** become eligible for removal in the first revision
released on or after 2027-07-28. The old **HTTP+SSE** transport has been deprecated
since 2025-03-26 and is on a shorter clock: three months after SEP-2596 reaches Final.

**Course structure:** five core labs fit the 3-hour format - Jumpstart, Building
Servers & the Wire Protocol, Security, MRTR, and Replicas. Labs 6-8 are an
**optional track** (composition → IDE integration → multiple servers) for rooms
that move fast; each builds on the one before it.

**The one idea to hold on to:** the protocol no longer remembers anything between
requests. Any state that outlives a single call is now an explicit identifier that
the server hands out and the client passes back. That is what makes MCP servers
horizontally scalable - and, as a bonus, it makes state visible to the model instead
of hiding it inside the transport.

> **A note on versions.** These labs run on **FastMCP 4.0.0b1**, which is a *beta*. It
> is the only FastMCP release that speaks `2026-07-28`; The version is pinned exactly in
> `requirements.txt` on purpose.
>

</br></br>

---

**Lab 1 - MCP Jumpstart**

**Purpose: In this lab, we'll see how to go from hand-rolled API calls to an MCP implementation.**

1. For our labs in this workshop, we have different directories with related code. For this lab, it is the *lab1* directory. Change into that directory in the terminal.
   
```
cd lab1
```
<br><br>

2. Let's first create a simple code example to invoke an API math function in the "classic" way - using a raw REST call.
   In the terminal, run the first command below to create a new file called *classic_calc.py*. 

```
code classic_calc.py
```
</br></br>

3. Here's the code for our simple API call. Paste the code below into the *classic_calc.py* file.
   
```
import requests, urllib.parse, sys

expr = urllib.parse.quote_plus("12*8")
url  = f"https://api.mathjs.org/v4/?expr={expr}"
print("Calling:", url)
print("Result :", requests.get(url, timeout=10).text)
```

![Creating classic_calc.py](./images/mcp4.png?raw=true "Creating classic_calc.py")
</br></br>

4. Save your changes (CTRL/CMD/OPTION + S). Now, run the code using the command below. You should see the expected answer (96) printed out. Notice that you needed to **know the endpoint, URL-encode the call, and parse the response** yourself. This is only for one tool, but imagine doing this for multiple tools.

```
python classic_calc.py
```
<br><br>

5. Now, let's see how we can use an MCP server to do this. There is an existing MCP server for simple calculator functions that we're going to be using in this lab.  It uses the streamable http transport. The code is in GitHub at https://github.com/skillrepos/calculator-mcp if you are interested. Start a running instance of the server by using *npx* (a Node.js CLI). We'll start it running on port 8931. Run the command below and you should see output like the screenshot shown.

```
npx -y github:skillrepos/calculator-mcp --port 8931
```

![Running remote MCP server](./images/mcp152.png?raw=true "Running remote MCP server")
<br><br>

6. Now, let's open an additional terminal so we can run our custom code. You can use the "+" control in the upper right of the terminal to add a new terminal or just split the terminal. As shown here, we're splitting the terminal by clicking on the "down arrow" to the immediate right of the plus and selecting *Split terminal*.

![Splitting terminal](./images/mcp96.png?raw=true "Splitting terminal")
<br><br>

7. Let's see how we can create a minimal client to use the MCP server. Create a new file called *mcp_client.py* with the first command. We'll add code for this in the next step.

```
code mcp_client.py
```
</br></br>

8. Now paste the code below into the file. Make sure to save your changes when done.

```
import asyncio
from fastmcp import Client

async def main():
    # The URL alone is enough - FastMCP picks the Streamable HTTP transport.
    # Note there is NO trailing slash: /mcp is the canonical endpoint form.
    async with Client("http://127.0.0.1:8931/mcp") as client:
        # In 2026-07-28 there is no initialize handshake. mode="auto" (the
        # default) probes with server/discover and falls back to the older
        # handshake if the server is from an earlier protocol era.
        print("Negotiated protocol version:", client.protocol_version)

        # Discover available tools
        tools = await client.list_tools()
        print("Discovered tools:", [t.name for t in tools])

        # Invoke 'mul' without worrying about HTTP, auth, or schemas
        result = await client.call_tool("mul", {"a": 12, "b": 8})

        # FastMCP 4 returns a CallToolResult object, not a bare list.
        # .data is the hydrated Python value when the server returns
        # structured content; text-only servers (like this one) populate
        # .content instead, so fall back to the first content block.
        print("12 x 8 =", result.data or result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```
<br><br>

9. Notice that within this code we didn't have to code in endpoint formats, juggle query strings, or handcraft JSON schemas. Also, the server advertises all tools dynamically. In the second terminal, run the client with the command below and you should see output similar to the screenshot below. 

```
python mcp_client.py
```

![Running client](./images/mcp159.png?raw=true "Running client")

</br></br>

   Look at the first line of output - the **negotiated protocol version**. This is worth a moment. The calculator server is a third-party server that may well have been written against an older revision of MCP. Our client asked for `2026-07-28`; if the server can't speak it, the client falls back to the older handshake-based protocol. You'll see whichever version the two of them actually agreed on. Under the new spec, version negotiation happens **per request** rather than once at connection time, which is what makes this kind of graceful fallback possible.
</br></br>

10. Finally, let's build out a simple agent implementation that uses tools from this server in conjunction with a local LLM to respond to a prompt. We'll assemble the agent code again using the *diff and merge* approach. Run the command below and you can scroll down through the differences and merge them in to complete the code. When done, just click the "X" in the tab at the top to close this view.

```
code -d ../extra/agent_mcp.txt agent_mcp.py
```

![Diff view](./images/mcp155.png?raw=true "Diff view")
</br></br>

   As you merge, notice what this agent is and is not. There is **no agent framework here** - no LangChain, no CrewAI. An agent is just a loop: ask the server what tools exist, hand those schemas to the model, run whatever the model asks for, feed the results back, repeat. Pay particular attention to `to_ollama_tools()`. That function is the M x N problem in miniature: MCP handed us a standard tool description, and we adapt it *once* for whichever model vendor we happen to be using. Without MCP you would be writing that adapter for every tool *and* every model.
</br></br>

11. Now, you can run the agent to see it in action. When this runs, it will show you the LLM's output and also the various tool calls and results. Note that it will take a while for the LLM to process things since it is running against a local model in our codespace. Also, since we are not using a very powerful or tuned model here, it is possible that you will see a mistake in the final output. If so, try running the agent code again. (Notice that we are using a different problem this time: 12x8/3)

```
python agent_mcp.py
```

![agent answer](./images/mcp154.png?raw=true "agent answer")

</br></br>

12. You can stop the MCP server in the original terminal via CTRL-C.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 2 - Building MCP Servers and the Protocol on the Wire**

**Purpose: In this lab, we'll build a complete MCP server from scratch - tools, a static resource, a resource template, and a prompt, held together by explicit state handles - and then look at the raw 2026-07-28 protocol it speaks on the wire.**

### Part A - Build and explore the server

1. Change into the *lab2* directory. In this directory, we have a partially implemented note-taking MCP server. Open the file and take a quick look at the skeleton - you'll see TODO comments where the implementations will go.

```
cd ../lab2
code note_server.py
```
<br><br>

   Before merging, read the comment block at the top of the file. This lab's server is where the stateless redesign becomes concrete. In earlier MCP revisions you could keep a `notes` dictionary at module level and rely on the session to tell you which client's notes were which. **You can't do that any more** - there's no session, and the next request may land on a different instance behind a load balancer.

   The replacement is an **explicit handle**: the server mints an identifier, returns it as ordinary data, and the client passes it back on every call.
<br><br>

2. Now let's use the diff-merge approach to complete the implementation. Run the command below to open a side-by-side view of the completed code alongside the skeleton.

```
code -d ../extra/note_server.txt note_server.py
```

![Merging notes server](./images/mcp127.png?raw=true "Merging notes server")

<br><br>

3. Merge each section by hovering over the middle bar and clicking the arrows pointing right. As you merge, you are assembling all four of the essential MCP element types in one server:

   - **Handle minting** (`open_notebook`) - returns an unguessable `handle`. This is the 2026-07-28 replacement for an implicit session.
   - **Tools** (`save_note`, `list_notes`) - these *do work*, and they take the handle as an ordinary argument. Notice that this means the **model can see the handle** and carry it forward in the conversation. State that used to hide in the transport is now part of the dialogue.
   - **Static resource** (`resource://catalog`) - a fixed URI. 2026-07-28 forbids list results from varying *per connection*, but they **may** still vary by the authorization presented on the request - filtering a tool list by the caller's scopes is explicitly allowed, because credentials are per-request input rather than connection state. Ours is caller-independent simply because this lab has no authentication.
   - **Resource template** (`resource://note/{handle}/{title}`) - a *dynamic* URI. The handle rides in the URI, which is the resource-side equivalent of passing it as an argument.
   - **Prompt** (`summarize_notes`) - assembles a notebook's notes into an LLM-ready prompt.

   Also notice `cache_ttl=60, cache_scope="private"` in the constructor. Under 2026-07-28, six operations **must** carry caching hints (`ttlMs`/`cacheScope`): `server/discover`, the four list calls, and `resources/read`. Ours is `"private"` because notebook contents vary per user - a shared proxy must never serve one user's cached listing to another.

   When all sections are merged and there are no more differences, close the tab to save the file.
<br><br>

4. Start the server.

```
python note_server.py
```

![Running note server](./images/mcp128.png?raw=true "Running note server")

<br><br>

5. Open a second terminal and start the MCP Explorer to interact with the server. (Adjust the path if you're not in /workspaces/mcp.)

```
python scripts/mcp_explorer.py http://localhost:8000/mcp 5000
```

   Click *Open in Browser* when the popup appears. Before clicking anything else, look at the status line at the top: it shows the **negotiated protocol version** and the server's name. That connection involved no handshake - the Explorer sent a single `server/discover` request, the new mandatory-for-servers RPC that returns supported versions, capabilities and instructions in one round trip.

![Starter MCP explorer](./images/mcp129.png?raw=true "Starter MCP explorer")

<br><br>

6. In the Explorer, click on *Tools*. You'll see `open_notebook`, `save_note` and `list_notes`. Start by calling `open_notebook` with `name`: "lab2". **Copy the `handle` value out of the result** - you'll need it for every following call.

![Using a tool](./images/mcp160.png?raw=true "Using a tool")

<br><br>

   Now call `save_note` with your handle, `title`: "meeting-summary" and `content`: "Discussed MCP architecture and decided to use server composition." Then save a second note with the same handle, `title`: "action-items" and `content`: "Build gateway server and connect to IDE."

   Then call `list_notes` with the handle to see both titles.
<br><br>

   Now let's see what "the handle is not a session" really means. Call `list_notes` again, but change one character in the middle of the handle. You'll get a clean error rather than someone else's data.

   This is the spec's **State Handle Hijacking** guidance in action: possessing a handle is **not** authentication. Handles must be unguessable (ours uses `secrets.token_urlsafe`) and, in production, bound server-side to the authenticated user - so that even a *correct* handle from the wrong user is refused. A guessable, unbound handle would be strictly worse than the session it replaced.
<br><br>

7. Now click on *Resources*. Under **Resources** there's `resource://catalog` (the static resource). Click *Read Resource* on it to see the open notebooks. Below that, under **Resource Templates**, you'll see `resource://note/{handle}/{title}`. To read a single note, type a concrete URI into the URI field - substituting your handle - and click *Read Resource*:

```
resource://note/YOUR_HANDLE_HERE/meeting-summary
```

   Notice the difference: the catalog is caller-independent, while the template URI resolves to exactly one note in exactly one notebook.
<br><br>

![resources](./images/mcp133.png?raw=true "resources")

<br><br>

   Click on *Prompts* and use the *Get Prompt* button to get the `summarize_notes` prompt, passing your handle as the argument. You'll see it has assembled both of your saved notes into a single prompt ready for an LLM. This is the pattern: tools write data, resources expose it, prompts package it for LLMs.

![prompts](./images/mcp134.png?raw=true "prompts")

<br><br>

### Part B - The protocol on the wire

8. The Explorer is convenient, but it hides the protocol. Let's strip away the tooling and look at what actually goes over HTTP - against the server **you just built**. Leave note_server.py running, and stop the Explorer (CTRL+C in its terminal) or open a third terminal. From the *lab2* directory, run the probe script:

```
cd lab2   (if needed)
./wire_probe.sh
```

![Wire probe output](./images/mcp166.png?raw=true "Wire probe output")
<br><br>

9. Work through the output section by section. **Section 1** is the `server/discover` response. Find these fields:

   - `supportedVersions` - which protocol revisions this server speaks
   - `capabilities` - what it offers, including the new `extensions` map
   - `resultType: "complete"` - **every** result now carries this. The other possible value is `"input_required"`, which we'll meet in Lab 4.
   - `ttlMs: 60000` and `cacheScope: "private"` - the caching hints from your server's constructor
   - `_meta` containing `io.modelcontextprotocol/serverInfo`
<br><br>

   Now look at what was *sent*. Open the script to see the request bodies:

```
code wire_probe.sh
```

   Every request carries a `_meta` block containing `io.modelcontextprotocol/protocolVersion` and `io.modelcontextprotocol/clientCapabilities`. In earlier revisions those were negotiated once, during `initialize`, and remembered for the life of the session. There is no session now, so they ride along on every single request. That is the whole idea: **any request can be handled by any server instance, with no shared state and no sticky routing.**
<br><br>

   Look at the HTTP headers on each `curl`. Three are mandatory:

   | Header | When required | Mirrors | New? |
   |---|---|---|---|
   | `MCP-Protocol-Version` | Every request | `_meta` protocol version | Existed since 2025-06-18; what's new is that it MUST match the body |
   | `Mcp-Method` | Every request | the JSON-RPC `method` | New in 2026-07-28 (SEP-2243) |
   | `Mcp-Name` | `tools/call`, `resources/read`, `prompts/get` | `params.name` or `params.uri` | New in 2026-07-28 (SEP-2243) |

   Why duplicate what's already in the body? So that a gateway, load balancer, or WAF can route, rate-limit, and authorize **per tool** without parsing JSON. Your infrastructure can now say "only the analytics tier may call `execute_sql`" using a plain header rule.
<br><br>

10. **Section 4** shows the catch. The script deliberately sends `Mcp-Name: list_notes` while the body says `open_notebook`. You should see **HTTP 400** and JSON-RPC error **-32020** (`HeaderMismatch`).

   This matters more than it looks. If a load balancer routed on the header while the server executed the body, an attacker could route past your policy and still run whatever they wanted. The spec closes that by requiring the component that actually executes the request to re-validate that the headers agree with the body.
<br><br>

   **Section 5** asks for protocol version `1999-01-01`. You get **-32022** (`UnsupportedProtocolVersion`) with a `data.supported` list. This is how a client discovers what to retry with - there's no handshake to negotiate during, so the error itself carries the negotiation.
<br><br>

   **Section 6** does a plain `GET` on the endpoint and gets a 4xx. In 2025-11-25 and earlier, `GET` opened a standing SSE stream that the server used to push requests and notifications at the client. That stream is gone. A server that wants to push change notifications now waits for the client to open a `subscriptions/listen` request, whose *response* is the long-lived stream.
<br><br>

11. One last thing to notice about the whole run: **the order didn't matter.** No call depended on any earlier call. There was nothing to open and nothing to close. That's the property the entire revision was designed around.
<br><br>

   In preparation for other labs, you can stop (CTRL+C) the running instance of note_server.py in your terminal to free up port 8000. You can also close the browser tab that has the explorer running in it.

<br><br>

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 3 - Security and Authorization in MCP**

**Purpose: In this lab, we'll stand up an authorization server and a protected MCP server, and walk the full OAuth 2.1 discovery chain that a 2026-07-28 client is required to follow.**

1. Change into the *lab3* directory in the terminal.
   
```
cd ../lab3
```
<br><br>


2. In this directory, we have an authorization server, a secure MCP server, and a client. These are teaching stand-ins - they use a shared HS256 secret so the lab runs offline, where production would use asymmetric keys published via JWKS - but the *protocol flow* is the real one.

   To look at the code, open any of the files by clicking on them in the explorer view to the left in the codespace, or use the "code <filename>" command in the terminal. The numbered comments in each file highlight the key parts.

</br></br>   

| **File**               | **What to notice**                                                             |
|------------------------|--------------------------------------------------------------------------------|
| **[`auth_server.py`](lab3/auth_server.py)**   | Publishes RFC 8414 metadata; mints tokens whose **audience is the MCP server's canonical URI** |
| **[`secure_server.py`](lab3/secure_server.py)** | `JWTVerifier` + `RemoteAuthProvider` - validates audience, enforces scopes, publishes RFC 9728 resource metadata |
| **[`secure_client.py`](lab3/secure_client.py)** | Walks the chain by hand: 401 to resource metadata to AS metadata to token to call |

</br></br>

3. Start the **authorization** server with the command below and leave it running in that terminal.

```
python auth_server.py
```

![Running authentication server](./images/mcp58.png?raw=true "Running authentication server") 
<br><br>

4. Switch to another terminal (or open a new one with the "+" above the terminals) and start the secure **MCP** server. Make sure you're in the *lab3* directory.

```
cd lab3    (if needed)
python secure_server.py
```

![start secure server](./images/mcp156.png?raw=true "start secure server")

<br><br>


5. Open another new terminal and send a request with no token, to see the challenge. Note that we're sending a proper 2026-07-28 request, with the `_meta` block and the required headers.

```
cd lab3

curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -H "MCP-Protocol-Version: 2026-07-28" \
     -H "Mcp-Method: tools/list" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}'
```

![401 error](./images/mcp157.png?raw=true "401 error") 
<br><br>

   You get a **401**, but look at the `WWW-Authenticate` header rather than just the status code:

```
WWW-Authenticate: Bearer scope="calc:add", resource_metadata="http://127.0.0.1:8000/.well-known/oauth-protected-resource/mcp"
```

   The spec requires the 401 to tell the client **where to find out more**. This is the entry point of the whole discovery chain, and it means a client that has never seen this server before can authenticate against it with no prior configuration.
<br><br>

6. Follow that URL yourself. This is the RFC 9728 **Protected Resource Metadata** document:

```
curl -s http://127.0.0.1:8000/.well-known/oauth-protected-resource/mcp | jq
```

   Note `resource` (this server's canonical URI) and `authorization_servers` (who can issue tokens for it). The client now knows who to go ask.
<br><br>

7. Next hop - the authorization server's own metadata (RFC 8414):

```
curl -s http://127.0.0.1:9000/.well-known/oauth-authorization-server | jq
```

   Three fields here are worth calling out, because all three are emphasized in 2026-07-28:

   - **`code_challenge_methods_supported`** - PKCE. A client **must** verify `S256` is offered and **must refuse to proceed** if this field is missing.
   - **`authorization_response_iss_parameter_supported`** - RFC 9207. The authorization server identifies itself on the response, and the client compares it against the issuer it expected *before* redeeming the code. This closes **authorization server mix-up attacks**, which PKCE alone does *not* prevent.
   - **`client_id_metadata_document_supported`** - CIMD. 2026-07-28 **deprecates Dynamic Client Registration** in favor of Client ID Metadata Documents, where the `client_id` is simply an HTTPS URL that resolves to a JSON metadata document. It's portable: no re-registering with every authorization server you meet.
<br><br>

8. Now run the client, which walks all of these hops and then calls the tool. You'll see each step printed.

```
python secure_client.py
```

![Running the secure client](./images/mcp59.png?raw=true "Running the secure client") 
<br><br>

9. In step [4] of the output, notice the token is bound to an audience: `http://127.0.0.1:8000/mcp`. That comes from the RFC 8707 `resource` parameter the client sent with its token request. **This is the most important security rule in MCP:** a server **must** reject any token that was not issued *for it*, and a server that calls an upstream API **must not** pass the client's token through - it obtains its own.

   Without that rule you get the **confused deputy** problem: your MCP server happily spends a token that was minted for somebody else, and the downstream API trusts it because your server vouched for it.
<br><br>

10. Let's prove the audience check is real. Get a token bound to a *different* resource and try to use it:

```
curl -s -X POST "http://127.0.0.1:9000/token?resource=http://example.com/other-server" \
     -d "username=demo-client&password=demopass" | jq -r .access_token > /tmp/wrong_aud.txt

curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Authorization: Bearer $(cat /tmp/wrong_aud.txt)" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -H "MCP-Protocol-Version: 2026-07-28" \
     -H "Mcp-Method: tools/list" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}'
```

   The token is perfectly valid - correctly signed, unexpired, issued by an authorization server this MCP server trusts. It is rejected anyway, because it wasn't minted for *this* resource.
<br><br>

   Finally, show that a corrupted token fails too:

```
export TOKEN=$(curl -s -X POST "http://127.0.0.1:9000/token?resource=http://127.0.0.1:8000/mcp" \
     -d "username=demo-client&password=demopass" | jq -r .access_token)

curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Authorization: Bearer ${TOKEN}corruption" \
     -H "Content-Type: application/json" \
     -H "Accept: application/json, text/event-stream" \
     -H "MCP-Protocol-Version: 2026-07-28" \
     -H "Mcp-Method: tools/list" \
     -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{}}}}'
```

   (Optional) If you want to look deeper at a valid token, `echo $TOKEN` and paste the value into https://jwt.io, or introspect it:

```
curl -s -X POST http://127.0.0.1:9000/introspect \
     -H "Content-Type: application/json" \
     -d "{\"token\":\"$TOKEN\"}" | jq
```

![Introspecting token](./images/mcp62.png?raw=true "Introspecting token") 
<br><br>

11. One structural point before we leave this lab. Per-request authorization is not new - earlier revisions already required the `Authorization` header on *every* HTTP request, explicitly including requests that were part of the same logical session. What changed is that there is no longer a session for a token to be associated with at all. The token, the protocol version, the capabilities and the caller's identity now travel together on every request, and nothing about the connection carries meaning.
<br><br>

   When you're done, you can stop (CTRL+C) the running authorization server and the secure MCP server.
   
<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 4 - Multi Round-Trip Requests (asking the user a question)**

**Purpose: In this lab, we'll build a tool that needs information from the user partway through executing, using the MRTR pattern that replaced server-initiated requests.**

1. Here's the problem. A tool often needs something it wasn't given: a confirmation, a missing parameter, a choice between options. In MCP revisions up through 2025-11-25, the server solved this by sending a JSON-RPC **request** back to the client over an SSE stream it was holding open (`elicitation/create`).

   That requires a live bidirectional connection, which requires the client to stay pinned to one server instance - which is exactly what the stateless redesign removed. So 2026-07-28 replaced it with **Multi Round-Trip Requests (MRTR)**.
<br><br>

   The MRTR shape is: the server never initiates anything. Instead it **responds** to the client's request saying "I need more input":

   1. Client sends `tools/call` (id 1).
   2. Server responds with `resultType: "input_required"`, carrying `inputRequests` (what it needs) and an opaque `requestState` (what it wants to remember).
   3. Client gathers the answers, then **re-sends the original request with a new id**, adding `inputResponses` and echoing `requestState` back untouched.
   4. Server returns the final `"complete"` result.

   Because everything the server needs travels in that retry, **the retry can land on a completely different server instance and still work.**
<br><br>

2. Change into the *lab4* directory and open the skeleton.

```
cd ../lab4
code trip_server.py
```
<br><br>

3. Read the comment block at the top, then merge in the completed implementation.

```
code -d ../extra/trip_server.txt trip_server.py
```
<br><br>

4. As you merge, notice the shape of the tool. It is called **twice** for one logical operation, and it branches on `ctx.input_responses`:

   - **First call**: `ctx.input_responses` is `None`, so the tool returns an `InputRequiredResult` describing what it needs.
   - **Second call**: the client has re-sent the request with answers attached, so `ctx.input_responses` is populated and the tool does the real work.

   This is called the **guard pattern**, and it's the thing most likely to trip you up when migrating an existing server. `ctx.elicit()` still *compiles* under FastMCP 4, and it still works on legacy connections - but it **raises at runtime** on a 2026-07-28 connection. If you have elicitation in your own servers, this is what you'll need to change.
<br><br>

   Notice also `request_state_security=RequestStateSecurity(keys=[SIGNING_KEY])` in the server constructor. `requestState` is opaque to the client, which must echo it back without reading or modifying it. But "the client can't read it" is not the same as "the client can't tamper with it" - so the spec requires servers to **integrity-protect** it, since it can influence authorization and business logic. FastMCP signs it for you when you supply a key. In a real multi-replica deployment, every replica must share that key, or a retry landing on a different instance would be rejected.
<br><br>

5. Start the server.

```
python trip_server.py
```
<br><br>

6. In a second terminal, look at the client before running it.

```
cd lab4
code trip_client.py
```

   The client side is refreshingly simple: register an `elicitation_handler` and FastMCP drives the entire MRTR loop for you - it notices `input_required`, calls your handler once per requested input, then re-sends the original call with the answers and the echoed `requestState`. The same handler also answers server-pushed elicitations on legacy connections, so one handler covers both protocol eras.
<br><br>

7. Run the client. It will ask you for a traveler name, then have you pick a flight.

```
python trip_client.py
```

![MRTR booking flow](./images/mcp161.png?raw=true "MRTR booking flow")
<br><br>

8. Now switch to the terminal running the server and look at its request log. You'll see **more than one `POST /mcp`** for what was, from your point of view, a single `book_trip` call. Each of those POSTs is an entirely independent HTTP request. There is no connection being held open between them and no server-side memory linking them - only the signed `requestState` blob that traveled out and came back.

    That's the whole point: put four replicas behind a round-robin load balancer and this still works, unchanged.
<br><br>

9. Try declining. Run the client again, and when it asks you to choose a flight, enter something invalid (like `99`). The handler declines, and the server reports a cancelled booking rather than crashing.

    The spec requires servers to handle this: a user is always allowed to say no. An `ElicitResult` carries an `action` of `"accept"`, `"decline"` or `"cancel"`, and only `"accept"` comes with content.

![Declining an elicitation](./images/mcp162.png?raw=true "Declining an elicitation")
<br><br>

10. Two limits worth remembering:

    - Only `tools/call`, `resources/read` and `prompts/get` may return `input_required`. No other request can.
    - A server **must not** ask for an input type the client didn't declare support for in its per-request capabilities. Ask an elicitation-less client to elicit and you get `-32021` (`MissingRequiredClientCapability`).
<br><br>

   Finally - MRTR isn't only for questions to users. The same mechanism carries `sampling/createMessage` (borrowing the client's LLM) and `roots/list`. Note, though, that **Sampling and Roots are both deprecated** as of 2026-07-28, with removal possible in any revision on or after 2027-07-28. Elicitation is the one that survives, which is why we built the lab around it.
<br><br>

   Stop the server with CTRL+C when you're done.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 5 - Running Replicas**

**Purpose: In this lab, we'll put two copies of a server behind a real round-robin load balancer and watch the 2026-07-28 model earn its keep: in-memory state breaks, MRTR survives, and a mismatched signing key shows why replicas must share one.**

1. Change into the *lab5* directory and look at the three server-side files. These are complete (no merging in this lab) - open each and read the header comments.

```
cd ../lab5
```

| **File**               | **What it is**                                                             |
|------------------------|-----------------------------------------------------------------------------|
| **[`replica_lb.py`](lab5/replica_lb.py)**   | A ~50-line round-robin load balancer. Deliberately dumb: no sessions, no JSON parsing - it just rotates and logs the `Mcp-Method` / `Mcp-Name` headers it sees. |
| **[`memory_server.py`](lab5/memory_server.py)** | The **anti-pattern**: a notebook server keeping handles in an in-memory dict - Lab 2's design, run the way you must never run it. |
| **[`replica_server.py`](lab5/replica_server.py)** | The Lab 4 TripBooker made replica-ready: port from the command line, per-replica logging, signing key from `REQUEST_STATE_KEY`. |

<br><br>

### Part A - Watch in-memory state break

2. You'll need **four terminals** for this lab (use the "+" / split controls as in earlier labs). In the first three, start two replicas of the *memory* server and the load balancer:

```
Terminal 1:   cd lab5 && python memory_server.py 8001
Terminal 2:   cd lab5 && python memory_server.py 8002
Terminal 3:   cd lab5 && python replica_lb.py 8000
```

   Note what the replicas print at startup: *"handles live ONLY in this process."* That's the bug, announced in advance.
<br><br>

3. In the fourth terminal, run the client. It opens a notebook, then tries to save into it **twice with the identical call**:

```
cd lab5
python handle_client.py
```

![In-memory state breaking behind the load balancer](./images/mcp163.png?raw=true "In-memory state breaking behind the load balancer")

   One `save_note` succeeds and one fails with *"Unknown notebook handle ... In-memory state does not survive load balancing."* Which attempt fails depends purely on where the round-robin happened to send it. Look at the two replica terminals: the handle exists in one process's memory and not the other's.
<br><br>

4. This is worth sitting with, because it's the classic production symptom: **intermittent** failure. Same handle, same call, different replica, different outcome. Nothing is wrong with the handle - the *state behind it* isn't reachable from every replica. The fix is exactly what the deck's replica diagram shows: move the store somewhere shared (Redis, a database), keyed `user:handle`. The protocol did its job - it made the state's address explicit; where you keep the state is yours to get right.
<br><br>

### Part B - Watch MRTR survive the same setup

5. Stop the two memory servers (CTRL+C in terminals 1 and 2 - **leave the load balancer running**) and start two replicas of the trip server in their place:

```
Terminal 1:   python replica_server.py 8001
Terminal 2:   python replica_server.py 8002
```
<br><br>

6. Now run the **unchanged Lab 4 client** from the fourth terminal. It still points at port 8000 - which is now the load balancer, not a server. The client cannot tell the difference, and that is itself the lesson:

```
cd ../lab4
python trip_client.py
```

   Answer the traveler and flight prompts as in Lab 4.
<br><br>

7. Look at the two replica terminals. You should see the two halves of ONE logical call handled by DIFFERENT processes:

```
[replica-8001] round 1: asking for inputs, returning signed requestState
[replica-8002] round 2: verified requestState signature, finishing the booking
```

![One MRTR call spanning two replicas](./images/mcp164.png?raw=true "One MRTR call spanning two replicas")

   And the final result names the finisher: `Booked ... [finished on replica-8002]`. Replica 8002 had never seen this conversation - everything it needed arrived inside `requestState`, carried (unread) by the client. This is the exact flow the memory server couldn't survive, succeeding for the exact reason Lab 4 taught.
<br><br>

   Glance at the load balancer terminal, too. It routed every request knowing only two HTTP headers:

```
[lb] POST /mcp  Mcp-Method=tools/call Mcp-Name=book_trip  ->  http://127.0.0.1:8001
[lb] POST /mcp  Mcp-Method=tools/call Mcp-Name=book_trip  ->  http://127.0.0.1:8002
```

   That's the Lab 2 routing-headers story in action: per-tool routing and metering with no JSON parsing anywhere.
<br><br>

### Part C - Why replicas must share the signing key

8. Stop replica 8002 (CTRL+C in terminal 2) and restart it with a **different** signing key:

```
REQUEST_STATE_KEY="a-different-key-on-this-replica!" python replica_server.py 8002
```
<br><br>

9. Run `python trip_client.py` again (answer the prompts). Whenever the two rounds straddle the two replicas, the retry is rejected:

```
MCPError: Invalid or expired requestState
```

![Mismatched signing key rejection](./images/mcp165.png?raw=true "Mismatched signing key rejection")

    Run it a couple of times and you'll see it succeed when both rounds happen to land on the same replica and fail when they don't - **intermittent again**, which is why this is such an unpleasant bug to chase in production. The rule it teaches: `requestState` is integrity-protected, so every replica must hold the same signing key, distributed the way you distribute any shared secret.
<br><br>

10. When you're done, stop everything (CTRL+C in each terminal). Three takeaways to carry out of this lab:

    - A load balancer in front of 2026-07-28 MCP servers can be completely MCP-ignorant - rotation plus optional header logging is the whole job.
    - State either travels with the request (`requestState`, handles) or lives somewhere every replica can reach. In-process memory is neither.
    - The two failure modes you saw - unknown handle, invalid requestState - are both *intermittent* under round-robin. If you ever see a "sometimes" bug behind an MCP load balancer, you now know the first two things to check.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

---

**The remaining three labs are an optional track for rooms that move fast. Each builds on the one before it: compose servers behind a gateway (Lab 6), connect that gateway to an IDE (Lab 7), then add a remote server alongside it (Lab 8).**

**Lab 6 - Composing MCP Servers (Optional)**

**Purpose: In this lab, we'll compose multiple focused servers behind a single gateway endpoint - the pattern production MCP deployments use.**

1. Change into the *lab6* directory and bring in the note server you completed in Lab 2 - the gateway will mount it alongside a new math server.

```
cd ../lab6
cp ../lab2/note_server.py .
```
<br><br>

2. We have a skeleton for a small math server. Merge the completed code into it using the same diff-merge approach as Lab 2:

```
code -d ../extra/math_server.txt math_server.py
```

Merge the changes (just two tools: `add` and `multiply`), then close the tab.

![math server merge](./images/mcp135.png?raw=true "math server merge")

<br><br>

3. Now let's build the *gateway* - a single server that mounts both servers behind one endpoint. Merge the completed code.

Notice the key lines: `gateway.mount(note_service, namespace="notes")` and `gateway.mount(math_service, namespace="math")`. (If you've used FastMCP 3, note that this parameter was called `prefix=` there and is `namespace=` now.)

```
code -d ../extra/gateway.txt gateway.py
```

![gateway server merge](./images/mcp136.png?raw=true "gateway server merge")


<br><br>

4. Start the gateway server. 

```
python gateway.py
```

![gateway server running](./images/mcp137.png?raw=true "gateway server running")

<br><br>

5. Start the Explorer as you did in Lab 2 (`python scripts/mcp_explorer.py http://localhost:8000/mcp 5000` from the repo root). This should connect to the gateway server on `http://localhost:8000/mcp`. Click on *Tools* and you'll see all tools from both servers, namespaced: `notes_open_notebook`, `notes_save_note`, `notes_list_notes`, `math_add`, `math_multiply`. Try calling `math_multiply` with `a`: 6 and `b`: 7 to confirm both servers are live. 

![all tools](./images/mcp138.png?raw=true "all tools")

<br><br>

6. Worth pausing on why this gateway pattern got easier in 2026-07-28. Under the old spec, a gateway in front of multiple replicas had to preserve session affinity - once a client did its `initialize` handshake against one instance, every later request had to come back to that same instance. With sessions gone, an ordinary round-robin load balancer works, with no shared session store. Combine that with the `Mcp-Method` and `Mcp-Name` headers from Lab 2 and your gateway can route and meter per tool without ever parsing a JSON body. (Lab 5's little load balancer was exactly this idea, live.)
<br><br>

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 7 - MCP in the Real World - IDE Integration (Optional)**

**Purpose: In this lab, we'll connect the gateway server from optional Lab 6 to VS Code's Copilot Chat. (Requires Lab 6.)**

1. First, we need a GitHub personal access token (PAT). When logged into GitHub, click on the link below, provide a note and click the green "Generate token" button at the bottom.

Link:  Generate classic personal access token (repo & workflow scopes) https://github.com/settings/tokens/new?scopes=repo,workflow

![Creating token](./images/mcp10.png?raw=true "Creating token")

![Creating token](./images/mcp87.png?raw=true "Creating token")
<br><br>

2. On the next screen, make sure to copy the generated token and save it for use later in the lab. You will not be able to see the actual token again!

![Copying token](./images/mcp11.png?raw=true "Copying token")
<br><br>

3. Make sure the gateway from Lab 6 is running. If you stopped it, restart it:

```
cd ../lab6
python gateway.py
```
<br><br>

4. Now let's create the IDE configuration that tells VS Code how to connect to our MCP server. Run the commands below. We'll start with just our local gateway - we'll add GitHub in a later step. (Switch to another terminal if needed.)

```
cd /workspaces/mcp
mkdir -p .vscode
cp extra/mcp_local_settings.json .vscode/mcp.json
code .vscode/mcp.json
```

Look at the file: `"type": "http"` tells VS Code to use the Streamable HTTP transport, and `"url"` points to our gateway. This is the same endpoint the Explorer has been connecting to. Note the URL has no trailing slash.
<br><br>

5. If the Copilot Chat panel is not already open, click on the Copilot icon at the top. Make sure it is in *Agent* mode via the drop-down at the bottom. (**NOTE:** If you don't see an option to switch modes, you may need to click the Copilot icon in the bottom status bar and click *Finish setup* first.)

![Opening chat panel](./images/mcp103.png?raw=true "Opening chat panel")

<br><br>

6. Now, in the *mcp.json* file, click the small *Start* link above the "Lab Gateway" server name. You should see it change to "√Running | Stop | Restart | N tools".


![Click start to connect](./images/mcp139.png?raw=true "Click start to connect")

![connection successful](./images/mcp140.png?raw=true "connection successful")


<br><br>

7. Click the small *Configure Tools...* icon in Copilot Chat. 

![Configure tools](./images/mcp141.png?raw=true "Configure tools")

<br><br>

8. In the dialog that opens up at the top of the session, you should see a list of connected tools/MCP servers. Find the one that says *Lab Gateway* and expand it. You should see the namespaced tools from your Lab 6 gateway: `notes_open_notebook`, `notes_save_note`, `notes_list_notes`, `math_add`, `math_multiply`.

![Lab Gateway tools](./images/mcp142.png?raw=true "Lab Gateway tools")

<br><br>

9. Try using your own tools from Copilot Chat. Because our note server uses explicit handles, start by asking for a notebook:

```
Open a notebook called "lab-notes" and tell me the handle
```

You'll probably have to *Allow* the operation.

![First tool prompt](./images/mcp143.png?raw=true "First tool prompt")

<br><br>

10. Now save a note. Notice you don't have to paste the handle back yourself - the model has it in its context from the previous turn and will pass it along:

```
Save a note in that notebook titled "lab-recap" with content "MCP lets AI agents discover and call tools dynamically."
```

![saved note](./images/mcp144.png?raw=true "saved note")

   **This is worth dwelling on.** Under the old session model, the "which notebook am I in?" state lived invisibly in the transport, and the model had no idea it existed. Now the handle is ordinary data in the conversation, so the model can hold on to it, pass it to the right calls, and even manage several notebooks at once. Making state explicit didn't just help the load balancer - it made the agent more capable.
<br><br>

11. You can also try another prompt to see more of the tools in action.

```
List all the notes in that notebook
```

![saved notes](./images/mcp145.png?raw=true "saved notes")

   Watch Copilot call the tools you built in Labs 2 and 6. Notice the "Ran notes_save_note" / "Ran math_multiply" confirmations in the output - these are *your* tools, running on *your* server.
<br><br>

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 8 - Using Multiple MCP Servers (Optional)**

**Purpose: In this lab, we'll add the remote GitHub MCP Server alongside our gateway server and look at the MCP Servers Marketplace.**


1. Let's add a second MCP server - the GitHub MCP Server - alongside our gateway. Copy in the full config and reopen:

```
cp extra/mcp_full_settings.json .vscode/mcp.json
code .vscode/mcp.json  (if not already open)
```

<br><br>

2.  You'll see two servers now: "Lab Gateway" (local) and "GitHub MCP Server" (remote). Click *Start* on the GitHub MCP Server - a dialog will pop up for you to paste in your PAT. Paste the token and hit *Enter*.

![Putting in PAT for token](./images/mcp146.png?raw=true "Putting in PAT for token")

<br><br>

3. Now Copilot has tools from *both* servers. Try a cross-server prompt:

```
Find the GitHub username for <your name>, then open a notebook and save it as a note titled "my-github-info"
```

   Watch Copilot call the GitHub search tool first, then call `notes_open_notebook` and `notes_save_note` with the result. This is multi-server orchestration - the LLM uses tools from different servers in a single conversation, all connected through the standard MCP protocol.

   Note that these two servers may not even be speaking the same protocol revision. Because version negotiation is now per request, a host can hold connections to a mix of modern and legacy servers at the same time without any of them having to agree with each other.

![combined operation](./images/mcp147.png?raw=true "combined operation")
   
<br><br>

4. Finally, click the *Extensions* icon on the left sidebar. You'll see a category for *MCP SERVERS - INSTALLED* showing both your Lab Gateway and the GitHub MCP Server.

![Connected servers](./images/mcp150.png?raw=true "Connected servers")

<br><br>

5. If you click on the magnifying glass icon on the upper right above the GitHub MCP server entry, you can approve access to see a broader list of available MCP servers.

![enable MCP Servers Marketplace](./images/mcp148.png?raw=true "enable MCP Servers Marketplace")

![Seeing list of MCP servers](./images/mcp149.png?raw=true "Seeing list of MCP servers")

   When you're done, you can stop the gateway with CTRL+C and close any extra tabs.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

---

## Appendix - Parts of 2026-07-28 we did not lab

These are real parts of the specification. They're left out of the hands-on labs
either because they're still settling, or because most people building an MCP server
will never touch them. They're listed here so you know they exist and know where the
edges are.

### Extensions

2026-07-28 formalized an **extensions framework** (SEP-2133). Extensions are named by
reverse-DNS (`io.modelcontextprotocol/tasks`), negotiated through a new `extensions`
field on capabilities, always opt-in, and versioned separately from the core spec.

| Extension | What it does | Status as of Aug 2026 |
|---|---|---|
| **MCP Apps** (`io.modelcontextprotocol/ui`) | Server-supplied HTML UI rendered in a sandboxed iframe in the host, communicating over `postMessage`. `ui://` resources can be prefetched. | Mature - shipped since Nov 2025, supported by several hosts |
| **Tasks** (`io.modelcontextprotocol/tasks`) | Long-running work via `tools/call` then `tasks/get` (poll) / `tasks/update` / `tasks/cancel`. Note there is deliberately **no `tasks/list`**, so one caller's tasks aren't enumerable by another. | SEP merged, but the reference implementation still self-labels experimental. Don't build production on the exact wire shapes yet. |
| **Enterprise Managed Authorization** | Enterprise IdP (Okta, Entra) issues an ID-JAG that the MCP authorization server exchanges for an access token. Centralized grant/revoke, no per-server user consent. | Documentation is inconsistent about stable vs draft. Requires IdP-side setup, not just client support. |
| **OAuth Client Credentials** | Machine-to-machine auth with no user present. | Draft |

### Subscriptions

`subscriptions/listen` replaces `resources/subscribe` and the old GET-based SSE stream.
The client opts in to specific notification types (`toolsListChanged`,
`promptsListChanged`, `resourcesListChanged`, `resourceSubscriptions`), the server
acknowledges with `notifications/subscriptions/acknowledged`, and every notification
carries `io.modelcontextprotocol/subscriptionId` in `_meta` so a client can
demultiplex several concurrent subscriptions. Stream resumability via `Last-Event-ID`
was **removed** - if the stream breaks, re-issue the request with a new id.

Our lab servers are static, so there is nothing to subscribe to. If you build a server
whose tool list changes at runtime, this is what you'll want.

### `Mcp-Param-*` routing headers (SEP-2243)

You can mark a primitive tool parameter with `"x-mcp-header": "Region"` in its input
schema, and clients will mirror that argument into an `Mcp-Param-Region` HTTP header.
This lets a gateway route or rate-limit on a *tool argument* - per tenant, per region -
without parsing the body. Restricted to primitive, statically-reachable properties (a MUST), and servers
**should not** mark sensitive parameters - passwords, API keys, tokens, PII - this way. Niche, but very useful if you operate a
multi-tenant MCP gateway.

### Observability

`traceparent`, `tracestate` and `baggage` are now reserved `_meta` keys carrying W3C
Trace Context, so MCP calls slot into OpenTelemetry traces directly. This is also the
recommended replacement for the deprecated Logging feature: log to `stderr` on stdio,
and use OpenTelemetry everywhere else.

### Backward compatibility

A single server can serve both eras at once. A "dual-era" client detects which it's
talking to: over stdio it probes with `server/discover`, and over HTTP it tries a
modern request and inspects the body of any `400`. A recognizable modern JSON-RPC error
means retry; an unrecognizable one (a legacy server answers `-32600 "Missing session
ID"` or `-32601 Method not found`) means fall back to `initialize`. FastMCP's
`Client(url, mode="auto")` - the default, and what these labs use - does all of this
for you.

Everything in this course is dual-era in practice, verified against a real
pre-2026 stack (FastMCP 3.4.5, spec 2025-11-25):

- **The lab servers** (FastMCP 4) still accept the old `initialize` handshake:
  a legacy client connects, gets a `Mcp-Session-Id`, negotiates down to its own
  revision, and calls tools normally. Nothing extra to configure.
- **The lab clients** (`Client(url)`) fall through automatically when pointed at
  an old server: they retry with `initialize` and report the negotiated legacy
  version via `client.protocol_version`.
- **The Explorer** (`scripts/mcp_explorer.py`) tries `server/discover` first and,
  on a legacy rejection, falls back to the `initialize` handshake and carries the
  `Mcp-Session-Id` header on every later call. The status bar tells you which era
  you landed in ("stateless" vs. "legacy mode").

The one thing that is *not* backward compatible by design is the wire probe in
Lab 2 - it speaks raw 2026-07-28 on purpose, so against an old server its very
first request is the `400` a dual-era client would use as its fallback signal.

<br><br>
**THE END**
