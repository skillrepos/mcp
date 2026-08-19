# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 8.6 - 08/19/26

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

1. Each lab has its own directory of related code. Change into *lab1*.

```
cd lab1
```
<br><br>

2. First we'll call a math API the "classic" way - a raw REST call. Create the file.

```
code classic_calc.py
```
<br><br>

3. Paste this into *classic_calc.py* and save (CTRL/CMD + S).

```
import requests, urllib.parse, sys

expr = urllib.parse.quote_plus("12*8")
url  = f"https://api.mathjs.org/v4/?expr={expr}"
print("Calling:", url)
print("Result :", requests.get(url, timeout=10).text)
```

![Creating classic_calc.py](./images/mcp4.png?raw=true "Creating classic_calc.py")
<br><br>

4. Run it - you should see 96. Note what you had to know to get it: the endpoint, the URL encoding, and the response format. For one tool.

```
python classic_calc.py
```
<br><br>

5. Now the MCP version. Start a prebuilt calculator MCP server on port 8931 and leave it running.

```
npx -y github:skillrepos/calculator-mcp --port 8931
```

![Running remote MCP server](./images/mcp152.png?raw=true "Running remote MCP server")
<br><br>

6. Open a second terminal for the client - use the "+" control, or the down-arrow beside it and *Split terminal*.

![Splitting terminal](./images/mcp96.png?raw=true "Splitting terminal")
<br><br>

7. Create the client file.

```
code mcp_client.py
```
<br><br>

8. Paste this in and save. Compare it against step 3: no endpoint, no query string, no hand-written schema.

```
import asyncio
from fastmcp import Client

async def main():
    # The URL alone is enough - FastMCP picks the transport.
    async with Client("http://127.0.0.1:8931/mcp") as client:
        print("Negotiated protocol version:", client.protocol_version)

        # The server tells us what it offers
        tools = await client.list_tools()
        print("Discovered tools:", [t.name for t in tools])

        result = await client.call_tool("mul", {"a": 12, "b": 8})

        # .data holds structured results; text-only servers use .content
        print("12 x 8 =", result.data or result.content[0].text)

if __name__ == "__main__":
    asyncio.run(main())
```
<br><br>

9. Run the client in the second terminal. The tool list it prints came from the server, not from your code.

```
python mcp_client.py
```

![Running client](./images/mcp159.png?raw=true "Running client")
<br><br>

10. Now build an agent that uses those tools with a local LLM. The HTTP calls and trace printing are already done for you in *agent_helpers.py* - what you merge in is the MCP loop itself. Assemble it with the *diff and merge* approach: scroll through the differences and merge in **every** one, then close the tab with the "X". The file will not run until all of them are merged.

```
code -d ../extra/agent_mcp.txt agent_mcp.py
```

![Diff view](./images/mcp167.png?raw=true "Diff view")
<br><br>

11. Run the agent. It prints each tool call and result, then a final answer. Give it a few minutes - the model runs locally in the codespace. (Different problem this time: 12 x 8 / 3.) If the answer is wrong, run it again; the local model is small.

```
python agent_mcp.py
```

![agent answer](./images/mcp154.png?raw=true "agent answer")
<br><br>

12. Stop the MCP server in the first terminal with CTRL-C.
<br><br>

**What just happened** - worth reading while the agent runs.

- **There is no agent framework here.** No LangChain, no CrewAI. An agent is a loop: ask the server what tools exist, hand the schemas to the model, run whatever it asks for, feed the results back, repeat.
- **`to_ollama_tools()` is the M x N problem in miniature.** MCP handed us one standard tool description, and we adapt it *once* for a model vendor - not once per tool, per model.
- **That "negotiated protocol version" line** is what your client and this third-party server agreed on. Your client asks for `2026-07-28` and falls back if the server is older, which is why an unfamiliar server just works.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 2 - Building MCP Servers and the Protocol on the Wire**

**Purpose: In this lab, we'll build a complete MCP server from scratch - tools, a static resource, a resource template, and a prompt, held together by explicit state handles - and then look at the raw 2026-07-28 protocol it speaks on the wire.**

### Part A - Build and explore the server

1. Change into *lab2* and open the skeleton note-taking server. The TODO comments mark where the implementations go.

```
cd ../lab2
code note_server.py
```
<br><br>

2. Open the diff view to complete the implementation.

```
code -d ../extra/note_server.txt note_server.py
```

![Merging notes server](./images/mcp127.png?raw=true "Merging notes server")
<br><br>

3. Merge in **every** difference - hover over the middle bar and click the right-pointing arrows - then close the tab to save. You're assembling all four MCP element types plus the handle that ties them together.

   - **Handle minting** (`open_notebook`) - returns an unguessable `handle` as ordinary data.
   - **Tools** (`save_note`, `list_notes`) - do work, and take the handle as a normal argument.
   - **Static resource** (`resource://catalog`) - a fixed URI.
   - **Resource template** (`resource://note/{handle}/{title}`) - a dynamic URI, handle in the path.
   - **Prompt** (`summarize_notes`) - packages a notebook's notes for an LLM.
<br><br>

4. Start the server.

```
python note_server.py
```

![Running note server](./images/mcp128.png?raw=true "Running note server")
<br><br>

5. In a second terminal, start the MCP Explorer, then click *Open in Browser*. The status line shows the negotiated protocol version and the server's name. (Adjust the path if you're not in /workspaces/mcp.)

```
python scripts/mcp_explorer.py http://localhost:8000/mcp 5000
```

![Starter MCP explorer](./images/mcp129.png?raw=true "Starter MCP explorer")
<br><br>

6. Click *Tools* and call `open_notebook` with `name`: "lab2". **Copy the `handle` out of the result** - every later call needs it.

![Using a tool](./images/mcp160.png?raw=true "Using a tool")
<br><br>

   Call `save_note` twice with that handle - `title` "meeting-summary" / `content` "Discussed MCP architecture and decided to use server composition.", then `title` "action-items" / `content` "Build gateway server and connect to IDE." Then call `list_notes` with the handle to see both.
<br><br>

7. Call `list_notes` once more, but change one character in the middle of the handle. You get a clean error rather than someone else's data.
<br><br>

8. Click *Resources* and *Read Resource* on `resource://catalog`. Then under **Resource Templates**, type a concrete URI with your handle substituted in and read that.

```
resource://note/YOUR_HANDLE_HERE/meeting-summary
```

![resources](./images/mcp133.png?raw=true "resources")
<br><br>

   Then click *Prompts* and *Get Prompt* on `summarize_notes`, passing your handle. It has packaged both notes into one LLM-ready prompt. Tools write data, resources expose it, prompts package it.

![prompts](./images/mcp134.png?raw=true "prompts")
<br><br>

### Part B - The protocol on the wire

9. Leave note_server.py running. Stop the Explorer (CTRL+C) or open a third terminal, then run the probe from *lab2* to see the raw HTTP with no SDK in the way.

```
cd lab2   (if needed)
./wire_probe.sh
```

![Wire probe output](./images/mcp166.png?raw=true "Wire probe output")
<br><br>

10. **Section 1** is the `server/discover` response. Find `supportedVersions`, `capabilities`, `resultType: "complete"`, `ttlMs: 60000`, `cacheScope: "private"`, and `_meta`. Then open the script to see what was actually sent.

```
code wire_probe.sh
```
<br><br>

   Every request carries its own `_meta` with the protocol version and client capabilities, plus three headers that mirror the body:

   | Header | When required | Mirrors |
   |---|---|---|
   | `MCP-Protocol-Version` | Every request | `_meta` protocol version |
   | `Mcp-Method` | Every request | the JSON-RPC `method` |
   | `Mcp-Name` | `tools/call`, `resources/read`, `prompts/get` | `params.name` or `params.uri` |
<br><br>

11. Check the last three sections, then stop the server with CTRL+C to free port 8000 and close the Explorer browser tab.

   - **Section 4** sends `Mcp-Name: list_notes` while the body says `open_notebook`: **HTTP 400**, error **-32020** (`HeaderMismatch`).
   - **Section 5** asks for version `1999-01-01`: **-32022** (`UnsupportedProtocolVersion`), with a `data.supported` list telling you what to retry with.
   - **Section 6** does a plain `GET`: a 4xx. The endpoint takes POST only.
<br><br>

**What just happened** - the ideas this lab was built to show.

- **The handle replaces the session.** A server keeps nothing between requests, so anything spanning calls is named explicitly and passed back. Because the handle is an ordinary tool argument, the model can see it and carry it forward - the state is part of the conversation rather than hidden in the transport.
- **A handle is not a credential.** Possessing one proves nothing. Handles must be unguessable (`secrets.token_urlsafe` here) and, in production, bound server-side to the authenticated user, so that even a *correct* handle from the wrong user is refused. That's the spec's **State Handle Hijacking** guidance.
- **Caching hints are mandatory** on `server/discover`, the four list calls, and `resources/read`. Ours is `"private"` because notebook contents vary per user - a shared proxy must never serve one user's listing to another. List results may vary by the authorization on a request, but never by connection.
- **The headers duplicate the body so infrastructure never has to parse JSON.** A gateway can route, rate-limit, or authorize *per tool* with a plain header rule. Section 4 is why the server that executes the request must re-validate that header and body agree - otherwise an attacker routes past your policy and runs something else.
- **Order never mattered.** No call depended on an earlier one, and nothing was opened or closed. That's the property the whole revision was designed around.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 3 - Security and Authorization in MCP**

**Purpose: In this lab, we'll stand up an authorization server and a protected MCP server, and walk the full OAuth 2.1 discovery chain that a 2026-07-28 client is required to follow.**

1. Change into the *lab3* directory.

```
cd ../lab3
```
<br><br>

2. This directory holds an authorization server, a secure MCP server, and a client. They're teaching stand-ins - a shared HS256 secret so the lab runs offline, where production would use asymmetric keys published via JWKS - but the *protocol flow* is the real one. Open any file to read its numbered comments.

| **File**               | **What to notice**                                                             |
|------------------------|--------------------------------------------------------------------------------|
| **[`auth_server.py`](lab3/auth_server.py)**   | Publishes RFC 8414 metadata; mints tokens whose **audience is the MCP server's canonical URI** |
| **[`secure_server.py`](lab3/secure_server.py)** | `JWTVerifier` + `RemoteAuthProvider` - validates audience, enforces scopes, publishes RFC 9728 resource metadata |
| **[`secure_client.py`](lab3/secure_client.py)** | Walks the chain by hand: 401 to resource metadata to AS metadata to token to call |

<br><br>

3. Start the **authorization** server and leave it running in that terminal.

```
python auth_server.py
```

![Running authentication server](./images/mcp58.png?raw=true "Running authentication server") 
<br><br>

4. In another terminal, start the secure **MCP** server from the *lab3* directory.

```
cd lab3    (if needed)
python secure_server.py
```

![start secure server](./images/mcp156.png?raw=true "start secure server")
<br><br>

5. In a third terminal, send a request with no token to see the challenge.

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

   You get a **401**. Look at the `WWW-Authenticate` header rather than the status code - it tells the client where to go next.

```
WWW-Authenticate: Bearer scope="calc:add", resource_metadata="http://127.0.0.1:8000/.well-known/oauth-protected-resource/mcp"
```
<br><br>

6. Follow that URL - the RFC 9728 **Protected Resource Metadata** document. Note `resource` (this server's canonical URI) and `authorization_servers` (who can issue tokens for it).

```
curl -s http://127.0.0.1:8000/.well-known/oauth-protected-resource/mcp | jq
```
<br><br>

7. Next hop - the authorization server's own metadata (RFC 8414). Find `code_challenge_methods_supported`, `authorization_response_iss_parameter_supported`, and `client_id_metadata_document_supported`.

```
curl -s http://127.0.0.1:9000/.well-known/oauth-authorization-server | jq
```
<br><br>

8. Now run the client, which walks every hop above and then calls the tool. Each step is printed as it happens.

```
python secure_client.py
```

![Running the secure client](./images/mcp59.png?raw=true "Running the secure client") 
<br><br>

9. In step [4] of the output, note the token's audience: `http://127.0.0.1:8000/mcp`. That came from the RFC 8707 `resource` parameter the client sent with its token request.
<br><br>

10. Prove the audience check is real. Get a token bound to a *different* resource and try to use it - correctly signed, unexpired, from an issuer this server trusts, and rejected anyway.

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

   A corrupted token fails too:

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

   (Optional) Introspect a valid token, or `echo $TOKEN` and paste it into https://jwt.io.

```
curl -s -X POST http://127.0.0.1:9000/introspect \
     -H "Content-Type: application/json" \
     -d "{\"token\":\"$TOKEN\"}" | jq
```

![Introspecting token](./images/mcp62.png?raw=true "Introspecting token") 
<br><br>

11. Stop the authorization server and the secure MCP server with CTRL+C.
<br><br>

**What just happened** - the security rules behind what you just ran.

- **The 401 bootstraps everything.** Because the challenge names where to find the metadata, a client that has never seen this server before can authenticate against it with no prior configuration.
- **Three fields in the AS metadata carry weight.** `code_challenge_methods_supported` is PKCE - a client **must** verify `S256` is offered and refuse to proceed if the field is missing. `authorization_response_iss_parameter_supported` is RFC 9207: the authorization server identifies itself on the response and the client checks it *before* redeeming the code, which closes **authorization server mix-up attacks** that PKCE alone does not prevent. `client_id_metadata_document_supported` is CIMD, where a `client_id` is just an HTTPS URL resolving to a JSON metadata document - portable, with no re-registering at every authorization server. CIMD replaces Dynamic Client Registration.
- **Audience binding is the most important security rule in MCP.** A server **must** reject any token not issued *for it*, and a server that calls an upstream API **must not** pass the client's token through - it obtains its own. Without that you get the **confused deputy**: your server spends a token minted for somebody else, and the downstream API trusts it because your server vouched for it.
- **Nothing about the connection carries meaning.** The token, the protocol version, the capabilities and the caller's identity all travel together on every single request. There is no session for a token to be attached to.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 4 - Multi Round-Trip Requests (asking the user a question)**

**Purpose: In this lab, we'll build a tool that needs information from the user partway through executing, using the MRTR pattern that replaced server-initiated requests.**

1. A tool often needs something it wasn't given - a confirmation, a missing parameter, a choice between options. MCP handles that with **Multi Round-Trip Requests (MRTR)**, in which the server never initiates anything:

   1. Client sends `tools/call` (id 1).
   2. Server responds with `resultType: "input_required"`, carrying `inputRequests` (what it needs) and an opaque `requestState` (what it wants to remember).
   3. Client gathers the answers, then **re-sends the original request with a new id**, adding `inputResponses` and echoing `requestState` back untouched.
   4. Server returns the final `"complete"` result.
<br><br>

2. Change into the *lab4* directory and open the skeleton.

```
cd ../lab4
code trip_server.py
```
<br><br>

3. Merge in **every** difference, then close the tab to save.

```
code -d ../extra/trip_server.txt trip_server.py
```
<br><br>

4. Notice the shape as you merge. The tool is called **twice** for one logical operation and branches on `ctx.input_responses` - `None` on the first call, populated on the retry. That's the **guard pattern**.
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

   Register an `elicitation_handler` and FastMCP drives the whole loop for you: it notices `input_required`, calls your handler once per requested input, then re-sends the original call with the answers and the echoed `requestState`.
<br><br>

7. Run the client. It will ask you for a traveler name, then have you pick a flight.

```
python trip_client.py
```

![MRTR booking flow](./images/mcp161.png?raw=true "MRTR booking flow")
<br><br>

8. Switch to the terminal running the server and look at its request log. You'll see **more than one `POST /mcp`** for what was, from your side, a single `book_trip` call - each one an entirely independent HTTP request.
<br><br>

9. Run the client again and enter something invalid (like `99`) at the flight prompt. The handler declines and the server reports a cancelled booking rather than crashing.

![Declining an elicitation](./images/mcp162.png?raw=true "Declining an elicitation")
<br><br>

10. Stop the server with CTRL+C when you're done.
<br><br>

**What just happened** - why MRTR is shaped this way.

- **The server never initiates.** A server that pushes requests to a client needs a live bidirectional connection, and that pins the client to one instance. Under MRTR everything the server needs travels in the retry instead - so the retry can land on a completely different instance and still work. Put four replicas behind a round-robin load balancer and this is unchanged.
- **`requestState` is opaque, but not trusted.** The client echoes it back without reading or modifying it - but "the client can't read it" is not "the client can't tamper with it," so the spec requires servers to **integrity-protect** it. `request_state_security=RequestStateSecurity(keys=[SIGNING_KEY])` signs it for you. Every replica must share that key, or a retry landing elsewhere is rejected. Lab 5 shows exactly what that failure looks like.
- **The guard pattern is the migration gotcha.** `ctx.elicit()` still compiles under FastMCP 4 and still works on legacy connections, but **raises at runtime** on a 2026-07-28 connection.
- **Declining is required behavior.** An `ElicitResult` carries an `action` of `"accept"`, `"decline"` or `"cancel"`, and only `"accept"` comes with content. A user is always allowed to say no.
- **Two limits.** Only `tools/call`, `resources/read` and `prompts/get` may return `input_required`. And a server **must not** ask for an input type the client didn't declare support for - doing so returns `-32021` (`MissingRequiredClientCapability`).
- **MRTR isn't only for user questions.** The same mechanism carries `sampling/createMessage` (borrowing the client's LLM) and `roots/list` - both of which are deprecated, which is why this lab is built on elicitation.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 5 - Running Replicas**

**Purpose: In this lab, we'll put two copies of a server behind a real round-robin load balancer and watch the 2026-07-28 model earn its keep: in-memory state breaks, MRTR survives, and a mismatched signing key shows why replicas must share one.**

1. Change into *lab5*. These three files are complete - no merging in this lab.

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

2. You'll need **four terminals** for this lab. In the first three, start two replicas of the *memory* server and the load balancer. Note what the replicas print at startup: *"handles live ONLY in this process."*

```
Terminal 1:   cd lab5 && python memory_server.py 8001
Terminal 2:   cd lab5 && python memory_server.py 8002
Terminal 3:   cd lab5 && python replica_lb.py 8000
```
<br><br>

3. In the fourth terminal, run the client. It opens a notebook, then saves into it **twice with the identical call** - one succeeds, one fails. Check the two replica terminals: the handle exists in one process's memory and not the other's.

```
cd lab5
python handle_client.py
```

![In-memory state breaking behind the load balancer](./images/mcp163.png?raw=true "In-memory state breaking behind the load balancer")
<br><br>

### Part B - Watch MRTR survive the same setup

4. Stop the two memory servers (CTRL+C in terminals 1 and 2 - **leave the load balancer running**) and start two replicas of the trip server in their place.

```
Terminal 1:   python replica_server.py 8001
Terminal 2:   python replica_server.py 8002
```
<br><br>

5. Run the **unchanged Lab 4 client** from the fourth terminal. It still points at port 8000 - which is now the load balancer, not a server. The client cannot tell the difference.

```
cd ../lab4
python trip_client.py
```
<br><br>

6. Look at the two replica terminals. One logical call, two different processes:

```
[replica-8001] round 1: asking for inputs, returning signed requestState
[replica-8002] round 2: verified requestState signature, finishing the booking
```

![One MRTR call spanning two replicas](./images/mcp164.png?raw=true "One MRTR call spanning two replicas")

   The load balancer terminal shows what it needed to know to route all that - two headers, no JSON:

```
[lb] POST /mcp  Mcp-Method=tools/call Mcp-Name=book_trip  ->  http://127.0.0.1:8001
[lb] POST /mcp  Mcp-Method=tools/call Mcp-Name=book_trip  ->  http://127.0.0.1:8002
```
<br><br>

### Part C - Why replicas must share the signing key

7. Stop replica 8002 (CTRL+C in terminal 2) and restart it with a **different** signing key.

```
REQUEST_STATE_KEY="a-different-key-on-this-replica!" python replica_server.py 8002
```
<br><br>

8. Run `python trip_client.py` again and answer the prompts. When the two rounds straddle the two replicas, the retry is rejected. Run it a couple of times - it succeeds when both rounds land on the same replica.

```
MCPError: Invalid or expired requestState
```

![Mismatched signing key rejection](./images/mcp165.png?raw=true "Mismatched signing key rejection")
<br><br>

9. Stop everything with CTRL+C in each terminal.
<br><br>

**What just happened** - three things to carry out of this lab.

- **Both failures you saw were *intermittent*.** Same handle, same call, different replica, different outcome. That's the classic production symptom, and it's why these are unpleasant bugs to chase. If you ever see a "sometimes" failure behind an MCP load balancer, unknown-handle and invalid-requestState are the first two things to check.
- **State either travels with the request or lives somewhere every replica can reach.** `requestState` and handles travel; in-process memory does neither. The protocol did its job by making the state's address explicit - where you *keep* that state is yours to get right (Redis, a database, keyed `user:handle`).
- **The load balancer can be completely MCP-ignorant.** Rotation plus optional header logging is the whole job. No session table, no sticky routing, no JSON parsing - which is the entire point of the stateless design.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

---

**The remaining three labs are an optional track for rooms that move fast. Each builds on the one before it: compose servers behind a gateway (Lab 6), connect that gateway to an IDE (Lab 7), then add a remote server alongside it (Lab 8).**

**Lab 6 - Composing MCP Servers (Optional)**

**Purpose: In this lab, we'll compose multiple focused servers behind a single gateway endpoint - the pattern production MCP deployments use.**

1. Change into *lab6* and bring in the note server you completed in Lab 2 - the gateway will mount it alongside a new math server.

```
cd ../lab6
cp ../lab2/note_server.py .
```
<br><br>

2. Merge the completed code into the math server skeleton - just two tools, `add` and `multiply` - then close the tab.

```
code -d ../extra/math_server.txt math_server.py
```

![math server merge](./images/mcp135.png?raw=true "math server merge")
<br><br>

3. Now the gateway - one server that mounts both behind a single endpoint. As you merge, note the key lines: `gateway.mount(note_service, namespace="notes")` and `gateway.mount(math_service, namespace="math")`.

```
code -d ../extra/gateway.txt gateway.py
```

![gateway server merge](./images/mcp136.png?raw=true "gateway server merge")
<br><br>

4. Start the gateway.

```
python gateway.py
```

![gateway server running](./images/mcp137.png?raw=true "gateway server running")
<br><br>

5. Start the Explorer as in Lab 2 (`python scripts/mcp_explorer.py http://localhost:8000/mcp 5000` from the repo root) and click *Tools*. You'll see everything from both servers, namespaced: `notes_open_notebook`, `notes_save_note`, `notes_list_notes`, `math_add`, `math_multiply`. Call `math_multiply` with `a`: 6 and `b`: 7 to confirm both are live.

![all tools](./images/mcp138.png?raw=true "all tools")
<br><br>

**What just happened**

- **A gateway in front of replicas needs no session affinity.** An ordinary round-robin load balancer works, with no shared session store - Lab 5's little load balancer was exactly this idea, live.
- **Combine that with the `Mcp-Method` and `Mcp-Name` headers from Lab 2** and your gateway can route and meter per tool without ever parsing a JSON body.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 7 - MCP in the Real World - IDE Integration (Optional)**

**Purpose: In this lab, we'll connect the gateway server from optional Lab 6 to VS Code's Copilot Chat. (Requires Lab 6.)**

1. You'll need a GitHub personal access token. Click the link below, add a note, and click the green *Generate token* button at the bottom.

Link:  Generate classic personal access token (repo & workflow scopes) https://github.com/settings/tokens/new?scopes=repo,workflow

![Creating token](./images/mcp10.png?raw=true "Creating token")

![Creating token](./images/mcp87.png?raw=true "Creating token")
<br><br>

2. Copy the generated token and save it - you will not be able to see it again.

![Copying token](./images/mcp11.png?raw=true "Copying token")
<br><br>

3. Make sure the Lab 6 gateway is running. If you stopped it, restart it.

```
cd ../lab6
python gateway.py
```
<br><br>

4. Create the IDE configuration that tells VS Code how to reach the gateway. `"type": "http"` selects the Streamable HTTP transport and `"url"` is the same endpoint the Explorer used - note there's no trailing slash. (Switch to another terminal if needed.)

```
cd /workspaces/mcp
mkdir -p .vscode
cp extra/mcp_local_settings.json .vscode/mcp.json
code .vscode/mcp.json
```
<br><br>

5. Open the Copilot Chat panel with the Copilot icon at the top, and set it to *Agent* mode with the drop-down at the bottom. (If you don't see the mode options, click the Copilot icon in the bottom status bar and choose *Finish setup* first.)

![Opening chat panel](./images/mcp103.png?raw=true "Opening chat panel")
<br><br>

6. In *mcp.json*, click the small *Start* link above the "Lab Gateway" server name. It should change to "√Running | Stop | Restart | N tools".

![Click start to connect](./images/mcp139.png?raw=true "Click start to connect")

![connection successful](./images/mcp140.png?raw=true "connection successful")
<br><br>

7. Click the *Configure Tools...* icon in Copilot Chat, then find *Lab Gateway* in the dialog and expand it. You should see your namespaced Lab 6 tools: `notes_open_notebook`, `notes_save_note`, `notes_list_notes`, `math_add`, `math_multiply`.

![Configure tools](./images/mcp141.png?raw=true "Configure tools")

![Lab Gateway tools](./images/mcp142.png?raw=true "Lab Gateway tools")
<br><br>

8. Now use your own tools from Copilot Chat. You'll probably have to *Allow* the operation.

```
Open a notebook called "lab-notes" and tell me the handle
```

![First tool prompt](./images/mcp143.png?raw=true "First tool prompt")
<br><br>

9. Save a note. Notice you don't paste the handle back yourself - the model kept it from the previous turn and passes it along.

```
Save a note in that notebook titled "lab-recap" with content "MCP lets AI agents discover and call tools dynamically."
```

![saved note](./images/mcp144.png?raw=true "saved note")
<br><br>

10. One more, to see the rest of the tools in action. Watch for the "Ran notes_save_note" / "Ran math_multiply" confirmations - these are *your* tools, on *your* server.

```
List all the notes in that notebook
```

![saved notes](./images/mcp145.png?raw=true "saved notes")
<br><br>

**What just happened**

- **The handle was visible to the model the whole time.** Because state that spans calls is ordinary data in the conversation rather than something hidden in the transport, the model can hold onto it, pass it to the right calls, and manage several notebooks at once. Making state explicit didn't only help the load balancer - it made the agent more capable.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 8 - Using Multiple MCP Servers (Optional)**

**Purpose: In this lab, we'll add the remote GitHub MCP Server alongside our gateway server and look at the MCP Servers Marketplace.**

1. Add a second MCP server - the GitHub MCP Server - alongside the gateway.

```
cp extra/mcp_full_settings.json .vscode/mcp.json
code .vscode/mcp.json  (if not already open)
```
<br><br>

2. You'll see two servers now: "Lab Gateway" (local) and "GitHub MCP Server" (remote). Click *Start* on the GitHub MCP Server, paste your PAT into the dialog, and hit *Enter*.

![Putting in PAT for token](./images/mcp146.png?raw=true "Putting in PAT for token")
<br><br>

3. Copilot now has tools from *both* servers. Try a prompt that needs both - watch it call the GitHub search tool first, then `notes_open_notebook` and `notes_save_note` with the result.

```
Find the GitHub username for <your name>, then open a notebook and save it as a note titled "my-github-info"
```

![combined operation](./images/mcp147.png?raw=true "combined operation")
<br><br>

4. Click the *Extensions* icon in the left sidebar. Under *MCP SERVERS - INSTALLED* you'll see both your Lab Gateway and the GitHub MCP Server.

![Connected servers](./images/mcp150.png?raw=true "Connected servers")
<br><br>

5. Click the magnifying glass icon above the GitHub MCP Server entry to approve access and browse a broader list of available MCP servers. When you're done, stop the gateway with CTRL+C and close any extra tabs.

![enable MCP Servers Marketplace](./images/mcp148.png?raw=true "enable MCP Servers Marketplace")

![Seeing list of MCP servers](./images/mcp149.png?raw=true "Seeing list of MCP servers")
<br><br>

**What just happened**

- **That was multi-server orchestration.** One conversation, tools from two independent servers, connected through the same protocol - and the host needed no special knowledge of either.
- **The two servers need not speak the same protocol revision.** Version negotiation happens per request, so a host can hold connections to a mix of modern and older servers at once without any of them having to agree with each other.

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
