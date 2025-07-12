# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 1.11 - 07/12/25

**Versions of dialogs, buttons, etc. shown in screenshots may differ from current version used in dev environments**

**Follow the startup instructions in the README.md file IF NOT ALREADY DONE!**

**NOTES:**
1. We will be working in the public GitHub.com, not a private instance.
2. Chrome may work better than Firefox for some tasks.
3. Substitute the appropriate key combinations for your operating system where needed.
4. The default environment will be a GitHub Codespace (with everything you need already installed). If you prefer to use your own environment, you are responsible for installing the needed apps and dependencies in it. Some things in the lab may be different if you use your own environment.
5. To copy and paste in the codespace, you may need to use keyboard commands - CTRL-C and CTRL-V.**
6. VPNs may interfere with the ability to run the codespace. It is recommended to not use a VPN if you run into problems.
</br></br></br>

**Lab 1 - MCP Jumpstart**

**Purpose: In this lab, we'll see how to go from hand-rolled API calls to an MCP implementation.**

1. For our labs in this workshop, we have different directories with related code. For this lab, it is the *lab1* directory. Change into that directory in the terminal and take a look at the app's files.
   
```
cd lab1
```

2. Let's first create a simple code example to invoke an API math function in the "classic" way - using a raw REST call.
   In the terminal, run the first command below to create a new file called *classic_calc.py*. Then paste in the code shown into that file.

```
code classic_calc.py
```
</br></br>
```
import requests, urllib.parse, sys

expr = urllib.parse.quote_plus("12*8")
url  = f"https://api.mathjs.org/v4/?expr={expr}"
print("Calling:", url)
print("Result :", requests.get(url, timeout=10).text)
```
</br></br>
![Creating classic_calc.py](./images/mcp4.png?raw=true "Creating classic_calc.py")


3. Save your changes (CTRL/CMD/OPTION + S). Now, run the code using the command below. You should see the expected answer (96) printed out. Notice that you needed to know the endpoint, URL-encode the call, and parse the response yourself. This is only for one tool, but imagine doing this for multiple tools.

```
python classic_calc.py
```

4. Now, let's see how we can use an MCP server to do this. There is an existing MCP server for simple calculator functions that we're going to be using in this lab. It is named *calculator-mcp* from *wrtnlabs*. (The code for it is in GitHub at if you are interested at
 https://github.com/wrtnlabs/calculator-mcp if you are interested.) Start a running instance of the server by using *npx* (a Node.js CLI). We'll start it running on port 8931. Run the command below and you should see output like the screenshot shown.

```
npx -y @wrtnlabs/calculator-mcp@latest --port 8931
```

![Running remote MCP server](./images/mcp5.png?raw=true "Running remote MCP server")

5. Now, let's open an additional terminal so we can run our custom code. Right-click and select *Split terminal*.

![Splitting terminal](./images/mcp6.png?raw=true "Splitting terminal")

6. Let's see how we can create a minimal client to use the MCP server. Create a new file called *mpc_client.py* with the first command. Then paste in the code for it from the lines that follow.

```
code mcp_client.py
```
</br></br>
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

7. Notice that we didn't have to code in endpoint formats, juggle query strings, or handcraft JSON schemas. Also, the server advertises all tools dynamically. Run the client with the command below and you should see output similar to the screenshot below. 

```
python mcp_client.py
```
</br></br>
![Running client](./images/mcp7-new.png?raw=true "Running client")

8. Finally, let's create a simple agent implementation that uses tools from this server in conjunction with a local LLM to respond to a prompt.
   To save time, we already have the code for the agent in the file *agent_mcp.py*. You can browse the code to see what it is doing.
   To make it easier to see the differences from the simple client, run the command below and you can scroll down through the differences.
   *Do not make any changes in the files here.* When done, just click the "X" in the tab at the top to close this view.

```
code -d mcp_client.py agent_mcp.py
```
</br></br>
![Diff view](./images/mcp8.png?raw=true "Diff view")

9. Now, you can run the agent to see it in action. Note that it will take a while for the LLM to process things since it is running against a local model in our codespace.

```
python agent_mcp.py
```
</br></br>
![Running agent](./images/mcp9.png?raw=true "Running agent")

10. You can stop the MCP server in the original terminal via CTRL-C.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 2 - MCP Capabilities**

**Purpose: - In this lab, we'll use the Inspector tool to understand more about the different capabilities that can be provided by MCP servers**

1. Change into the *lab2* directory in the terminal.
   
```
cd lab2
```

2. In this directory, we have an example MCP server with tools, a prompt, and a resource.  It's designed as a "travel assistant" example. Open the file and take a look at the code. You can use the command below for that or click on it in the files list. The numbered comments highlight the key parts.

```
code mcp_travel_server.py
```

3. Now, let's start the server running. Issue the command below in the terminal. You should see the code start up and say it is running on localhost (127.0.0.1) and availale on port 8000.

```
python mcp_travel_server.py
```
</br></br>
![Running server](./images/mcp36.png?raw=true "Running server")


4. Now let's start the inspector. We have a script that will do that with the settings we need to use it in the codespace. Run the command below to get the processes going.

```
../scripts/start_mcpi.sh
```
</br></br>
![Copy URL](./images/mcp76.png?raw=true "Copy URL")


5. After this runs, there will be a URL printed at the end. Click on the link to open it or copy and paste the URL into a new browser tab. You should see the MCP Inspector displayed. **Click on the Connect button** to connect to the server.

**NOTE: When interacting with the inspector in the remaining steps, it may take a couple of seconds for the interface to respond after you click on an item in the UI.**

![Connecting](./images/mcp34.png?raw=true "Connecting")
   
7. If all goes well, you'll now be connected to the server. Now you can start exploring the various items the server makes available. First, let's look at the *Resources*. As shown in the screenshot, click on *Resources* in the top gray bar, then click on *List Resources*. This should show a resource named *major_cities*. Click on that and you should see a display of the actual resource as defined in the server we started earlier.

![Resources](./images/mcp27.png?raw=true "Resources") 

8. Next up, you can take a look at the prompt from the server. In the gray bar at the top of the inspector, click on *Prompts*, then *List Prompts* in the box below. You should see a prompt with the name of "recommend_sightseeing" listed. Click on that item and then you should see an item for that displayed to the right. In the box on the right, click on "Get Prompt" and you'll see the actual definition of the prompt.

![Prompt](./images/mcp28.png?raw=true "Prompt") 

9. Finally, let's take a look at the tools available from the server. Click on *Tools* in the gray bar, then *List Tools* in the box below. You'll see two tools defined - one to calculate distance and one to convert currency.

![Tools](./images/mcp37.png?raw=true "Tools") 

10. Let's try running the distance_between tool. Select the tool in the list. On the right side, you'll see the input fields for the tool. You can try any latitude and longitude values you want and then click "Run Tool" to see the results. (The example used in the screeshot - 40,74 and 51, .12 - equates roughly to New York and London.)

![Running tool](./images/mcp38.png?raw=true "Running tool") 

11. In preparation for other labs, you can stop (CTRL+C) the running instance of mcp_travel_server.py in your terminal to free up port 8000. You can also close the browser tab that has the inspector running in it.

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>


**Lab 3 - Security and Authorization in MCP**

**Purpose: In this lab, we'll demonstrate how to introduce an external authorization server and work with it to verify the difference between authorized and unauthorized requests when calling MCP tools.

1. Change into the *lab3* directory in the terminal.
   
```
cd lab3
```

2. In this directory, we have an example authorization server, a secure MCP server, and a secure MCP client. "Secure" here simply means they use a bearer token running on localhost, so they are not production-ready, but will serve us well for this lab. It's designed as a "travel assistant" example.  You can open any of the files by clicking on them in the explorer view to the left or using the "code <filename>" command in the terminal. The numbered comments in each file highlight the key parts. Also, the table under that suggests some things to notice about each.

</br></br>   

| **File**               | **What to notice**                                                             |
|------------------------|--------------------------------------------------------------------------------|
| **`auth_server.py`**   | `/token` issues a short-lived JWT; `/introspect` lets you verify its validity. |
| **`secure_server.py`** | Middleware rejects any request that’s missing a token or fails JWT verification.|
| **`secure_client.py`** | Fetches a token first, then calls the `add` tool with that bearer token.        |

</br></br>

3. Start the authorization server with the command below and leave it running in that terminal.

```
python auth_server.py
```

![Running authentication server](./images/mcp58.png?raw=true "Running authentication server") 

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

![curl and add new terminal](./images/mcp61.png?raw=true "curl and add new terminal") 

(Optional) If you want to look deeper at the token, you can grab the token string from the output and paste it in at https://jwt.io 

5. Now, in that terminal, start the secure server.

```
python secure_server.py
```

6. Open another new terminal (you can use the "+" again) and run the curl below to demonstrate that requests with no tokens fail. (When you run this you will see a "500 Internal Server Error" response. But if you switch back to the terminal where the server is running, you'll see that it's really a "401" error. It shows as a 500 error because the 401 is "swallowed" before it gets back to the client.

```
cd lab3 

curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":"bad","method":"list_tools","params":[]}'
```

![500 error and switching terminals](./images/mcp56.png?raw=true "500 error and switching terminals") 


7. Now in the same terminal, you can run the secure client. You should see output showing that it ran the "add" tool and the results. Behind the scenes it will have A) POSTed to /token B) Connected to /mcp  with Authorization: Bearer ...  C) Called the secure tool.

```
python secure_client.py
```

![Running the secure client](./images/mcp59.png?raw=true "Running the secure client") 

8. If you want, you can introspect the token we created with the curl command below.

```
curl -s -X POST http://127.0.0.1:9000/introspect \
     -H "Content-Type: application/json" \
     -d "{\"token\":\"$TOKEN\"}" | jq
```

![Introspecting token](./images/mcp62.png?raw=true "Introspecting token") 

9. Finally, you can show that breaking the token breaks the authentication. Run the curl command below. Then look back at the terminal with the authorization server running and you should see an error message.

```
BROKEN_TOKEN="${TOKEN}corruption"
curl -i -X POST http://127.0.0.1:8000/mcp \
     -H "Authorization: Bearer $BROKEN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","id":2,"method":"add","params":{"a":1,"b":1}}'
```

![Invalid token](./images/mcp63.png?raw=true "Invalid token") 

10. When you're done, you can stop (CTRL+C) the running authorization server and the secure mcp server.
   
<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 4 - Rapid Versioning and Rollback of MCP Tools**

**Purpose: In this lab, we'll see how to release, pin, and rollback MCP tool versions in minutes using the alias-delegation pattern, ensuring safe upgrades and fast recovery.

1. Change into the *lab4* directory in a terminal.
   
```
cd lab4
```

2. Take a quick look at the *server.py* file we have here. (You can click on the file or use the usual "code" command.) It implements a simple subtraction function for two integers. Notice that it uses an alias of "sub" to reference the underlying _sub_impl_v1 implementation function (version 1). After looking at it, *make sure you are in the TERMINAL* and you can start it running with the command below. Output will look like the screenshot (ignore the warnings).

```
python server.py
```
</br></br>

![Server startup](./images/mcp39.png?raw=true "Server startup") 


3. Now we can test the server by running a client. Switch to another terminal and make sure you are in the *lab4* directory. You can view the client code via the usual methods. When ready, make sure that you are in the TERMINAL and use the second command to run the client.

```
python client.py
```
</br></br>

You should see output that lists the tools and then calls the add tool to add the numbers. Note that both "sub_v1" and "sub" both exist.

![Client run](./images/mcp40.png?raw=true "Client run") 


4. Now, let's see how it looks if we introduce a different v2 version. Switch back to the terminal running the server and stop it with CTRL+C. We have a file *server_v2.py* with the v2 version of the subtraction routine.  We've also set the default to use v2. The v2 version has a subtle difference in the implementation. Take a look at the differences between the original server code and the v2 code via the command below. 

```
code -d server.py server_v2.py
```

5. You should see a side-by-side compare of the two files. When you're done looking, just click the "x" in the tab for the "server.py <-> server_v2.py" pane at the top to close the view.

![Server diff](./images/mcp64.png?raw=true "Server diff") 

6. Now, start the server_v2 code.

```
python server_v2.py
```

7. Switch to the other terminal and run the client again. This time you should see that it's calling the v2 version by default and we get a different answer.

```
python client.py
```
</br></br>

![New client run](./images/mcp42.png?raw=true "New client run") 
   
8. What if we wanted to pin to the previous (v1) version. We can do that easily. Here's some example code you can run (copy and paste and Enter) to demonstrate in the terminal using our existing server and client.

```
python - <<'PY'
import asyncio
from client import main

# Pin to sub_v1 explicitly
asyncio.run(main("sub_v1"))
PY
```
</br></br>

![Pin to v1](./images/mcp43.png?raw=true "Pin to v1") 

9. We can also see what happens if we try to use a version that doesn't exist with the code below. (Note the "sub_v3" reference.)

```
python - <<'PY'
import asyncio
from client import main

# Pin to sub_v1 explicitly
asyncio.run(main("sub_v3"))
PY
```
</br></br>
After running, you should see a "fastmcp.exceptions.ToolError: Unknown tool: sub_v3" message in the output.

![Pin to v3](./images/mcp44.png?raw=true "Pin to v3") 

10. (Optional) Suppose you later decide you don't want this function to continue to being used. You can add a [DEPRECATED] flag in the description by going back to the server_v2.py file and adding it on the line starting with "@mcp.tool(name="sub_v2")".  Then change the "Alias" section to point to "return _sub_impl_v1(a,b)" again. See screenshot for change.

![Deprecating v2](./images/mcp67.png?raw=true "Deprecating v2") 

11. (Optional) If you did step 10, you can start the updated server_v2 running with the usual python command again. Then switch over and run the client again. You should see that you get the v1 result and also the [DEPRECATED] banner shows up in the tool descriptions.

![Deprecated v2](./images/mcp68.png?raw=true "Deprecated v2")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 5 - Best Practices and Patterns for using MCP in Agents**

**Purpose: In this lab, we'll look at some best practices and patterns in implementing MCP in an agent.**

1. Change into the *lab5* directory in a terminal (and in any other terminals you use along the way).
   
```
cd lab5
```

2. For this lab, we need to make sure our local ollama server is running to serve the local llama3.2 LLM we'll be using. Check this by running the command below. If you see the output shown in the screenshot, you're good. Otherwise, if you see a message that Ollama is not running, you can start it with the command "ollama serve &".

```
ollama list
```
</br></br>
![Checking Ollama](./images/mcp48.png?raw=true "Checking Ollama")

3. In this directory, we have two partially implemented files - one for an MCP server named [**lab5/mcp_server.py**](./lab5/mcp_server.py) and one for an agent that uses the MCP server - named [**lab5/mcp_client_agent.py**](./lab5/mcp_client_agent.py). To complete the implementation in each of these, we're going to use an approach of doing a side-by-side diff of the completed code with our partial code and then merging the changes in to complete the implementation. Let's start with the server. For this lab, we have the outline of an agent in a file called *agent1.py* in that directory. 

```
code -d ../extra/mcp_server.txt mcp_server.py
```

4. Once you have run the command, you'll have a side-by-side view in your editor of the completed code and the mcp_server.py file. You can merge each section of code into the mcp_server.py file by hovering over the middle bar and clicking on the arrows pointing right. Go through each section, look at the code, and then click to merge the changes in, one at a time.

![Side-by-side merge](./images/mcp70.png?raw=true "Side-by-side merge") 

5. When you have finished merging all the sections in, the files should show no differences. Save the changes simply by clicking on the "X" in the tab name.

![Merge complete](./images/mcp71.png?raw=true "Merge complete") 

6. Now you can run your agent with the following command:

```
python mcp_server.py
```

7. Switch to another terminal and repeat the same process with the *mcp_client_agent.py* file. Review and merge in the changes, then save the changes by closing the tab at the top. Note in the code that tool names and model names and prompts are used as resources from the server, but LLM interaction is done in the client - as we would expect for a *real* agent.

```
code -d ../extra/mcp_client_agent.txt mcp_client_agent.py
```
</br></br>
![Side-by-side merge](./images/mcp73.png?raw=true "Side-by-side merge")

8. Once you've completed the merge and closed the tab, run the client and select one of the commands and ener some text for it. For example you might select the "expand" command and then enter some basic text like "MCP stands for Model Context Protocol." After a few moments you should see some output from the client.

```
python mcp_client_agent.py
```

![Trying out the client](./images/mcp74.png?raw=true "Trying out the client")

9. Optional: If you want, you can start up the MCP inspector again and see the resources in the server. To do this, you'll need to make sure the inspector is still running. If not or not sure, go ahead and run the command below as before. Then go to the URL it displays at the end and click *Connect*. After a few moments, it should connect to the server.

```
../scripts/start-inspector.sh
```

![Starting the inspector](./images/mcp77.png?raw=true "Starting the inspector")

10. If you did step 10, and got the server connected, you can click on the *Prompts* item in the top row and tell it to list the prompts. Due to some limitations, if you select *Get Prompts* you won't be able to see the full text of the prompt. You can also look at the resource with the model name, via the *Resources* option at the top. Finally, if you look at the *Tools* from the server, keep in mind that these are just wrappers around the prompts and won't actually change any text you enter.

![Running the inspector](./images/mcp75.png?raw=true "Running the inspector")

11. When done, you can stop the server via CTRL+C and the client via typing "exit" at a prompt. 


 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 6 - Connecting Applications to MCP Servers**

**Purpose: In this lab, we'll see how to connect GitHub Copilot to the GitHub MCP Server.**

1. For authentication to GitHub, we will need a GitHub personal access token (PAT). When logged into GitHub, click on the link below, provide a note and click the green "Generate token" button at the bottom.

Link:  Generate classic personal access token (repo & workflow scopes) https://github.com/settings/tokens/new?scopes=repo,workflow

![Creating token](./images/mcp10.png?raw=true "Creating token")
   
2. On the next screen, make sure to copy the generated token and save it for use later in the lab. You will not be able to see the actual token again!

![Copying token](./images/mcp11.png?raw=true "Copying token")

3. If the Copilot Chat panel is not already open, then click on the Copilot icon at the top. And/or if it is  not already in Agent mode at the bottom (says "Ask" or "Edit" instead), switch to *Agent* mode  via the drop-down at the bottom.

![Opening chat panel](./images/mcp69.png?raw=true "Opening chat panel")
<br>
![Switching to Agent mode](./images/mcp12.png?raw=true "Switching to Agent mode")

4. Now we need to add the GitHub MCP Server configuration in our IDE. You could fill most of this out via IDE prompts, but for simplicity, we already have a sample configuration file that we can just copy in. Run the commands below in the terminal. The last one will open the file in the editor.

```
cd /workspaces/mcp
mkdir .vscode
cp extra/mcp_github_settings.json  .vscode/mcp.json
code .vscode/mcp.json
```

5. Now, we can start the local MCP server. In the *mcp.json* file, above the name of the server, click on the small *Start* link (see figure below). A dialog will pop up for you to paste in your PAT. Paste the token in there and hit *Enter*. (Note that the token will be masked out.)

![Starting the server](./images/mcp23.png?raw=true "Starting the server")

After this, you should see the text above the server name change to "√Running | Stop | Restart | ## tools | More...".

![Starting the server](./images/mcp24.png?raw=true "Starting the server")

6. To see the tools that are available, in the Copilot Chat dialog, click on the small *tool* icon (see figure) and then scroll down to the *MCP Server: GitHub MCP Server* section. You'll see the available tools we picked up under that.

![Viewing available tools](./images/mcp25.png?raw=true "Viewing available tools")

7. Now that we have these tools available, we can use them in Copilot's Chat interface. (Again, you must be in *Agent* mode.) Here are some example prompts to try:

```
Find username for <your name> on GitHub
Show info on recent changes in skillrepos/mcp on GitHub
```
</br></br>

8. Notice the mention of "Ran <tool name> - GitHub MCP Server (MCP Server) early in the output for each.

![Example usage](./images/mcp26.png?raw=true "Example usage")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**THE END**

