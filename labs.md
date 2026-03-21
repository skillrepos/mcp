# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 5.0 - 03/21/26

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

5. Now, let's see how we can use an MCP server to do this. There is an existing MCP server for simple calculator functions that we're going to be using in this lab. It is named *calculator-mcp* from *wrtnlabs*. (The code for it is in GitHub at https://github.com/wrtnlabs/calculator-mcp if you are interested.) Start a running instance of the server by using *npx* (a Node.js CLI). We'll start it running on port 8931. Run the command below and you should see output like the screenshot shown.

```
npx -y @wrtnlabs/calculator-mcp@latest --port 8931
```

![Running remote MCP server](./images/mcp5.png?raw=true "Running remote MCP server")
<br><br>

6. Now, let's open an additional terminal so we can run our custom code. You can use the "+" control in the upper right of the terminal to add a new terminal or just split the terminal. As shown here, we're splitting the terminal by clicking on the "down arrow" to the immediate right of the plus and selecting *Split terminal*.

![Splitting terminal](./images/mcp96.png?raw=true "Splitting terminal")
<br><br>

7. Let's see how we can create a minimal client to use the MCP server. Create a new file called *mpc_client.py* with the first command. We'll add code for this in the next step.

```
code mcp_client.py
```
</br></br>

8. Now paste the code below into the file. Make sure to save your changes when done.

```
import asyncio
from fastmcp import Client

# latest version of FastMCP is async, so we need the async block
async def main():
    # The string URL is enough – FastMCP picks Streamable HTTP/SSE transport
    async with Client("http://127.0.0.1:8931/sse") as client:
        # Discover available tools
        tools = await client.list_tools()
        print("Discovered tools:", [t.name for t in tools])

        # invoke 'mul' w/o worrying about HTTP, auth, or schema
        result = await client.call_tool("mul", {"a": 12, "b": 8})
        print("12 × 8 =", result)        # → 96

if __name__ == "__main__":
    asyncio.run(main())
```
<br><br>

9. Notice that within this code we didn't have to code in endpoint formats, juggle query strings, or handcraft JSON schemas. Also, the server advertises all tools dynamically. In the second terminal, run the client with the command below and you should see output similar to the screenshot below. 

```
python mcp_client.py
```

![Running client](./images/mcp7-new.png?raw=true "Running client")
</br></br>

10. Finally, let's build out a simple agent implementation that uses tools from this server in conjunction with a local LLM to respond to a prompt. We'll assemble the agent code again using the *diff and merge* approach. Run the command below and you can scroll down through the differences and merge them in to complete the code. When done, just click the "X" in the tab at the top to close this view.

```
code -d ../extra/agent_mcp.txt agent_mcp.py
```

![Diff view](./images/ae60.png?raw=true "Diff view")
</br></br>

11. Now, you can run the agent to see it in action. When this runs, it will show you the LLM's output and also the various tool calls and results. Note that it will take a while for the LLM to process things since it is running against a local model in our codespace. Also, since we are not using a very powerful or tuned model here, it is possible that you will see a mistake in the final output. If so, try running the agent code again. (Notice that we are using a different problem this time: 12x8/3)

```
python agent_mcp.py
```

![Running agent](./images/mcp81.png?raw=true "Running agent")
</br></br>

12. You can stop the MCP server in the original terminal via CTRL-C.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 2 - MCP Features**

**Purpose: - In this lab, we'll use the Explorer tool to understand more about the different features that can be provided by MCP servers**

1. Change into the *lab2* directory in the terminal.
   
```
cd ../lab2
```
<br><br>

2. In this directory, we have an example MCP server with tools, a prompt, and a resource.  It's designed as a "travel assistant" example. Open the file and take a look at the code. You can use the command below for that or click on it in the files list. The numbered comments highlight the key parts.

```
code mcp_travel_server.py
```
<br><br>

3. Now, let's start the server running. Issue the command below in the terminal to run a startup script. You should see the code start up and say it is running on localhost (127.0.0.1) and availale on port 8000. (

```
python mcp_travel_server.py
```

![Running server](./images/mcp111.png?raw=true "Running server")
<br><br>


4. Let's use the MCP Explorer tool to look at items in the server. The server will be running in one terminal. In another terminal, start the explorer with the command below. Once it starts, you'll see a popup with a button to "*Open in Browser". Click on that to open it. (As shown the command assumes you are in the root directory. If not, use *../scripts* instead of *scripts*.)

```
python scripts/mcp_explorer.py http://localhost:8000/mcp 5000
```

![Start explorer](./images/mcp109.png?raw=true "Start explorer")
<br><br>


4. You should automatically be connected to the server. The *Prompts* item will be selected by default. (If the prompt is not shown, you can click on *List Prompts*.)

![Resources](./images/mcp110.png?raw=true "Resources") 
<br><br>


5. As shown in the *Arguments* section below the prompt text, this prompt takes a *city* as an argument. Click on the *Get Prompt* button and you'll see a dialog pop up at the top. It's asking for an argument to fill in to show what the instantiated prompt would look like. Enter the text below (note this is in JSON format).

```
{"city": "Paris"}
```

![Prompt](./images/mcp104.png?raw=true "Prompt") 
<br><br>

6. Click *OK* and you'll see the prompt result (with your argument) displayed.

![Completed prompt](./images/mcp105.png?raw=true "Completed prompt") 
<br><br>

7. Next, let's take a look at the resources available from the server. Click on the *Resources* button, then *Read Resource*. What you'll see is the resource with the major cities provided by the server.

![Resources](./images/mcp106.png?raw=true "Resources") 
<br><br>

8. Finally, let's take a look at the tools available from the server. Click on *Tools*. You'll see two tools defined - one to calculate distance and one to convert currency.

![Tools](./images/mcp112.png?raw=true "Tools") 
<br><br>


9. Let's try running the distance_between tool. Select the tool in the list. Underneath, you'll see the input fields for the tool. You can try any latitude and longitude values you want and then click *Execute to see the results. (The example used in the screeshot - 40,74 and 51, .12 - equates roughly to New York and London.)

![Running tool](./images/mcp113.png?raw=true "Running tool") 
<br><br>

10. In preparation for other labs, you can stop (CTRL+C) the running instance of mcp_travel_server.py in your terminal to free up port 8000. You can also close the browser tab that has the explorer running in it.

<br><br>

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 3 - Security and Authorization in MCP**

**Purpose: In this lab, we'll demonstrate how to introduce an external authorization server and work with it to verify the difference between authorized and unauthorized requests when calling MCP tools.

1. Change into the *lab3* directory in the terminal.
   
```
cd ../lab3
```
<br><br>


2. In this directory, we have an example authorization server, a secure MCP server, and a secure MCP client. "Secure" here simply means they use a bearer token running on localhost, so they are not production-ready, but will serve us for this lab. It's designed as a "travel assistant" example.

   To look at the code for the files, you can open any of them by clicking on them in the explorer view to the left in the codespace or click on the table item, or using the  "code <filename>" command in the terminal. The numbered comments in each file highlight the key parts. Also, the table below suggests some things to notice about each.

</br></br>   

| **File**               | **What to notice**                                                             |
|------------------------|--------------------------------------------------------------------------------|
| **[`auth_server.py`](lab3/auth_server.py)**   | `/token` issues a short-lived JWT; `/introspect` lets you verify its validity. |
| **[`secure_server.py`](lab3/secure_server.py)** | Middleware rejects any request that’s missing a token or fails JWT verification.|
| **[`secure_client.py`](lab3/secure_client.py)** | Fetches a token first, then calls the `add` tool with that bearer token.        |

</br></br>

3. Start the **authorization** server with the command below and leave it running in that terminal.

```
python auth_server.py
```

![Running authentication server](./images/mcp58.png?raw=true "Running authentication server") 
<br><br>

4. Switch to the other terminal or open a new one. (Over to the far right above the terminals is a "+" to create a new terminal.) Then, let's verify that our authorization server is working with the curl command below and save the token it generates for later use. Run the commands below in the split/new terminal. Afterwards you can echo $TOKEN if you want to see the actual value. (** Make sure to run the last two commands so your token env variable will be accessible in new terminals.**)

```
export TOKEN=$(
  curl -s -X POST \
       -d "username=demo-client&password=demopass" \
       http://127.0.0.1:9000/token \
  | jq -r '.access_token'        
)

echo "export TOKEN=$TOKEN" >> ~/.bashrc   
source ~/.bashrc 
```
</br></br>
![curl and add new terminal](./images/mcp95.png?raw=true "curl and add new terminal") 

(Optional) If you want to look deeper at the token, you can echo the token string and paste it in at https://jwt.io 
<br><br>


5. Now, in that second terminal, make sure you are in the *lab3* directory, and start the secure **mcp** server.

```
cd ../lab3 (if needed)
python secure_server.py
```
<br><br>


6. Open another new terminal (you can use the "+" again) and run the curl below to demonstrate that requests with no tokens fail. (When you run this you will see a "500 Internal Server Error" response. But if you switch back to the terminal where the server is running, you'll see that it's really a "401" error. It shows as a 500 error because the 401 is "swallowed" before it gets back to the client.

```
cd lab3 

curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":"bad","method":"list_tools","params":[]}'
```

![500 error and switching terminals](./images/mcp56.png?raw=true "500 error and switching terminals") 
<br><br>


7. Back in the terminal where you ran that last curl, you can run the secure client. You should see output showing that it ran the "add" tool and the results. Behind the scenes it will have A) POSTed to /token B) Connected to /mcp  with Authorization: Bearer ...  C) Called the secure tool.

```
python secure_client.py
```

![Running the secure client](./images/mcp59.png?raw=true "Running the secure client") 
<br><br>


8. If you want, you can introspect the token we created with the curl command below.

```
curl -s -X POST http://127.0.0.1:9000/introspect \
     -H "Content-Type: application/json" \
     -d "{\"token\":\"$TOKEN\"}" | jq
```

![Introspecting token](./images/mcp62.png?raw=true "Introspecting token") 
<br><br>


9. Finally, you can show that breaking the token breaks the authentication. Run the curl command below. 

```
BROKEN_TOKEN="${TOKEN}corruption"
curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Authorization: Bearer $BROKEN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":2,"method":"add","params":{"a":1,"b":1}}'
```
</br></br>
Then look back at the terminal with the secure server running and you should see an error message.
</br></br>

![Invalid token](./images/mcp63.png?raw=true "Invalid token") 

</br></br>

10. When you're done, you can stop (CTRL+C) the running authorization server and the secure mcp server.
   
<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 4 - Building and Composing MCP Servers**

**Purpose: In this lab, we'll build a real MCP server from scratch — with stateful tools, static and dynamic resources, and a prompt — then compose multiple servers behind a single gateway endpoint.**

1. Change into the *lab4* directory. In this directory, we have a partially implemented note-taking MCP server we have. Open the file and take a quick look at the skeleton — you'll see TODO comments where the implementations will go.

```
cd ../lab4
code note_server.py
```
<br><br>

2. Now let's use the diff-merge approach to complete the implementation. Run the command below to open a side-by-side view of the completed code alongside the skeleton.

```
code -d ../extra/note_server.txt note_server.py
```

![Merging notes server](./images/mcp127.png?raw=true "Merging notes server")

<br><br>

3. Merge each section by hovering over the middle bar and clicking the arrows pointing right. As you merge, notice the different kinds of MCP primitives being added:

   - **Tools** (`save_note`, `list_notes`) — these *do work*: they write to and read from an in-memory dictionary. Unlike the read-only tools in earlier labs, these change state on the server.
   - **Static resource** (`resource://notes/catalog`) — a fixed URI that always returns the full collection of notes.
   - **Resource template** (`resource://notes/{title}`) — a *dynamic* URI where `{title}` is resolved from what the client requests. This is how real MCP servers expose databases, file systems, and APIs.
   - **Prompt** (`summarize_notes`) — assembles all stored notes into an LLM-ready prompt.

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

   Click *Open in Browser* when the popup appears.

![Starter MCP explorer](./images/mcp129.png?raw=true "Starter MCP explorer")

<br><br>

6. In the Explorer, click on *Tools*. You'll see `save_note` and `list_notes`. Let's use them. Click *Call Tool* on `save_note` and enter values like `title`: "meeting-summary" and `content`: "Discussed MCP architecture and decided to use server composition." Click *Execute*. Then save a second note with `title`: "action-items" and `content`: "Build gateway server and connect to IDE."

![Using a tool](./images/mcp131.png?raw=true "Using a tool")

![Using a tool](./images/mcp132.png?raw=true "Using a tool")

<br><br>

7. Now click on *Resources*. You'll see two sections. Under **Resources** there's one entry — `resource://notes/catalog` (the static resource). Click *Read Resource* on it to see all your notes. Below that, under **Resource Templates**, you'll see `resource://notes/{title}` — this is a dynamic URI pattern. To read a single note, type `resource://notes/meeting-summary` into the URI field and click *Read Resource*. Notice the difference: the catalog always returns everything, while the template URI returns just the note matching the `{title}` you specified.
<br><br>

![resources](./images/mcp133.png?raw=true "resources")

8. Click on *Prompts* and get the `summarize_notes` prompt. You'll see it has assembled both of your saved notes into a single prompt ready for an LLM. This is the pattern: tools write data, resources expose it, prompts package it for LLMs.

![prompts](./images/mcp134.png?raw=true "prompts")

<br><br>

9. Now let's compose multiple servers. Stop the running note_server (CTRL+C). We also have a skeleton for a small math server. Merge the completed code into it the same way:

```
code -d ../extra/math_server.txt math_server.py
```

   Merge the changes (just two tools: `add` and `multiply`), then close the tab.

![math server merge](./images/mcp135.png?raw=true "math server merge")

<br><br>

10. Finally, let's build the *gateway* — a single server that mounts both servers behind one endpoint. Merge the completed code.

Notice the key lines: `gateway.mount(note_service, namespace="notes")` and `gateway.mount(math_service, namespace="math")`. This is how production MCP deployments work — separate, focused servers composed into one endpoint. 

```
code -d ../extra/gateway.txt gateway.py
```

![gateway server merge](./images/mcp136.png?raw=true "gateway server merge")


<br><br>

11. Start the gateway server. 

```
python gateway.py
```

![gateway server running](./images/mcp137.png?raw=true "gateway server running")

<br><br>

12. Restart the Explorer and connect to the gateway server on `http://localhost:8000/mcp`. Click on *Tools* and you'll see all tools from both servers, namespaced: `notes_save_note`, `notes_list_notes`, `math_add`, `math_multiply`. Try calling `math_multiply` with `a`: 6 and `b`: 7 to confirm both servers are live. When done, stop the gateway with CTRL+C. **Leave it stopped for now — we'll restart it in Lab 5.**

![all tools](./images/mcp138.png?raw=true "all tools")

<br><br>

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 5 - MCP in the Real World — IDE Integration**

**Purpose: In this lab, we'll connect the gateway server we built in Lab 4 to VS Code's Copilot Chat, then add a remote GitHub MCP Server alongside it to see multi-server orchestration in action.**

1. First, we need a GitHub personal access token (PAT). When logged into GitHub, click on the link below, provide a note and click the green "Generate token" button at the bottom.

Link:  Generate classic personal access token (repo & workflow scopes) https://github.com/settings/tokens/new?scopes=repo,workflow

![Creating token](./images/mcp10.png?raw=true "Creating token")

![Creating token](./images/mcp87.png?raw=true "Creating token")
<br><br>

2. On the next screen, make sure to copy the generated token and save it for use later in the lab. You will not be able to see the actual token again!

![Copying token](./images/mcp11.png?raw=true "Copying token")
<br><br>

3. Make sure the gateway from Lab 4 is running. If you stopped it, restart it:

```
cd ../lab4
python gateway.py
```
<br><br>

4. Now let's create the IDE configuration that tells VS Code how to connect to our MCP server. Run the commands below. We'll start with just our local gateway — we'll add GitHub in a later step.

```
cd /workspaces/mcp
mkdir -p .vscode
cp extra/mcp_local_settings.json .vscode/mcp.json
code .vscode/mcp.json
```

   Look at the file: `"type": "http"` tells VS Code to use streamable-HTTP transport, and `"url"` points to our gateway. This is the same endpoint the Explorer has been connecting to.
<br><br>

5. If the Copilot Chat panel is not already open, click on the Copilot icon at the top. Make sure it is in *Agent* mode via the drop-down at the bottom. (**NOTE:** If you don't see an option to switch modes, you may need to click the Copilot icon in the bottom status bar and click *Finish setup* first.)

![Opening chat panel](./images/mcp103.png?raw=true "Opening chat panel")

   Now, in the *mcp.json* file, click the small *Start* link above the "Lab Gateway" server name. You should see it change to "√Running | Stop | Restart | N tools".
<br><br>

6. Click the small *tool* icon in Copilot Chat. You should see the namespaced tools from your Lab 4 gateway: `notes_save_note`, `notes_list_notes`, `math_add`, `math_multiply`, plus the resources and prompt.
<br><br>

7. Try using your own tools from Copilot Chat. Type prompts like these (one at a time):

```
Save a note titled "lab-recap" with content "MCP lets AI agents discover and call tools dynamically."
```

```
List all my saved notes
```

```
What is 42 multiplied by 17?
```

   Watch Copilot call the tools you built in Lab 4. Notice the "Ran notes_save_note" / "Ran math_multiply" confirmations in the output — these are *your* tools, running on *your* server.
<br><br>

8. Now let's add a second MCP server — the GitHub MCP Server — alongside our gateway. Copy in the full config and reopen:

```
cp extra/mcp_full_settings.json .vscode/mcp.json
code .vscode/mcp.json
```

   You'll see two servers now: "Lab Gateway" (local) and "GitHub MCP Server" (remote). Click *Start* on the GitHub MCP Server — a dialog will pop up for you to paste in your PAT. Paste the token and hit *Enter*.
<br><br>

9. Now Copilot has tools from *both* servers. Try a cross-server prompt:

```
Find the GitHub username for <your name>, then save it as a note titled "my-github-info"
```

   Watch Copilot call the GitHub search tool first, then call `notes_save_note` with the result. This is multi-server orchestration — the LLM uses tools from different servers in a single conversation, all connected through the standard MCP protocol.
<br><br>

10. Finally, click the *Extensions* icon on the left sidebar. You'll see a category for *MCP SERVERS - INSTALLED* showing both your Lab Gateway and the GitHub MCP Server. If you click the globe icon, you can browse a list of additional MCP servers available in the marketplace — databases, cloud services, productivity tools, and more. Each one follows the same protocol your servers do.

![MCP Servers](./images/mcp98.png?raw=true "MCP Servers")

   When you're done, you can stop the gateway with CTRL+C and close any extra tabs.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

<br><br>
**THE END**

