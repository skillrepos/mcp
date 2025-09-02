# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 2.06 - 09/02/25

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

1. For our labs in this workshop, we have different directories with related code. For this lab, it is the *lab1* directory. Change into that directory in the terminal and take a look at the app's files.
   
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

6. Now, let's open an additional terminal so we can run our custom code. Right-click and select *Split terminal*.

![Splitting terminal](./images/mcp6.png?raw=true "Splitting terminal")
<br><br>

7. Let's see how we can create a minimal client to use the MCP server. Create a new file called *mpc_client.py* with the first command. Then paste in the code for it from the lines that follow. Save your changes when done.

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

9. Notice that within this code we didn't have to code in endpoint formats, juggle query strings, or handcraft JSON schemas. Also, the server advertises all tools dynamically. Run the client with the command below and you should see output similar to the screenshot below. 

```
python mcp_client.py
```

![Running client](./images/mcp7-new.png?raw=true "Running client")
</br></br>

10. Finally, let's create a simple agent implementation that uses tools from this server in conjunction with a local LLM to respond to a prompt.
   To save time, we already have the code for the agent in the file *agent_mcp.py*. You can browse the code to see what it is doing.
   To make it easier to see the **differences from the simple client**, run the command below and you can scroll down through the differences.
   *Do not make any changes in the files here.* When done, just click the "X" in the tab at the top to close this view.

```
code -d mcp_client.py agent_mcp.py
```

![Diff view](./images/mcp80.png?raw=true "Diff view")
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

**Purpose: - In this lab, we'll use the Inspector tool to understand more about the different features that can be provided by MCP servers**

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

3. Now, let's start the server running. Issue the command below in the terminal to run a startup script. You should see the code start up and say it is running on localhost (127.0.0.1) and availale on port 8000. (The startup script is used instead of a straight Python command because we need to ensure some environment variables are set to match what the inspector is using.)

```
../scripts/start_server.sh
```

![Running server](./images/mcp90.png?raw=true "Running server")
<br><br>


4. Let's use the MCP Inspector tool to look at items in the server. We have a script that will do that with the settings we need to use it in the codespace. In another terminal, run the command below to get the processes going. **After this runs, there will be a URL printed near the end.**

```
../scripts/start_inspector.sh
```

![Start inspector](./images/mcp94.png?raw=true "Start inspector")
<br><br>


5.  Click on the URL to open it (may need to hit Cmd or Option key and click) or copy and paste the URL into a new browser tab. You should see the MCP Inspector displayed. **Click on the Connect button** to connect to the server. (If you get a screen from GitHub warning about connecting to a codespace, just click *Continue*.)

![Confirmation](./images/mcp86.png?raw=true "Confirmation")
<br><br>
   

**If you can't get the inspector to connect, there are a couple of suggestions at the end of the script output. You can also try going to the PORTS tab, hovering over the "Port" column in the rows for port 6274 and 6277 and clicking "X" to remove them. Then run the *start_inspector.sh* script again.**

**NOTE: When interacting with the inspector in the remaining steps, it may take a couple of seconds for the interface to respond after you click on an item in the UI.**

![Connecting](./images/mcp34.png?raw=true "Connecting")
<br><br>

   
6. If all goes well, you'll now be connected to the server. Now you can start exploring the various items the server makes available. First, let's look at the *Resources*. As shown in the screenshot, click on *Resources* in the top gray bar, then click on *List Resources*. This should show a resource named *major_cities*. Click on that and you should see a display of the actual resource as defined in the server we started earlier.

![Resources](./images/mcp27.png?raw=true "Resources") 
<br><br>


7. Next up, you can take a look at the prompt from the server. In the gray bar at the top of the inspector, click on *Prompts*, then *List Prompts* in the box below. You should see a prompt with the name of "recommend_sightseeing" listed. Click on that item and then you should see an item for that displayed to the right. In the box on the right, click on "Get Prompt" and you'll see the specification of the prompt.

![Prompt](./images/mcp28.png?raw=true "Prompt") 
<br><br>


8. Finally, let's take a look at the tools available from the server. Click on *Tools* in the gray bar, then *List Tools* in the box below. You'll see two tools defined - one to calculate distance and one to convert currency.

![Tools](./images/mcp37.png?raw=true "Tools") 
<br><br>


9. Let's try running the distance_between tool. Select the tool in the list. On the right side, you'll see the input fields for the tool. You can try any latitude and longitude values you want and then click "Run Tool" to see the results. (The example used in the screeshot - 40,74 and 51, .12 - equates roughly to New York and London.)

![Running tool](./images/mcp38.png?raw=true "Running tool") 
<br><br>

10. In preparation for other labs, you can stop (CTRL+C) the running instance of mcp_travel_server.py in your terminal to free up port 8000. You can also close the browser tab that has the inspector running in it.

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


**Lab 4 - Best Practices and Patterns for using MCP in Agents**

**Purpose: In this lab, we'll look at some best practices and patterns in implementing MCP in an agent.**

1. Change into the *lab4* directory in a terminal (and in any other terminals you use along the way).
   
```
cd ../lab4
```

2. For this lab, we need to make sure our local ollama server is running to serve the local llama3.2 LLM we'll be using. Check this by running the command below. If you see the output shown in the screenshot, you're good. Otherwise, if you see a message that Ollama is not running, you can start it with the command "ollama serve &".

```
ollama list
```
</br></br>
![Checking Ollama](./images/mcp48-new.png?raw=true "Checking Ollama")

3. In this directory, we have two partially implemented files - one for an MCP server named [**lab4/mcp_server.py**](./lab4/mcp_server.py) and one for an agent that uses the MCP server - named [**lab4/mcp_client_agent.py**](./lab4/mcp_client_agent.py). The agent takes input text and then allows you to choose to have the text summarized, expanded or reworded by picking which option you want.
</br></br>
To complete the implementation in each of these files, we're going to use an approach of doing a side-by-side diff of the completed code with our partial code and then merging the changes in to complete the implementation. Let's start with the server build-out by using the command below. 

```
code -d ../extra/mcp_server.txt mcp_server.py
```

4. Once you have run the command, you'll have a side-by-side view in your editor of the completed code and the mcp_server.py file. You can merge each section of code into the mcp_server.py file by hovering over the middle bar and clicking on the arrows pointing right. Go through each section, look at the code, and then click to merge the changes in, one at a time.

![Side-by-side merge](./images/mcp70.png?raw=true "Side-by-side merge") 

5. When you have finished merging all the sections in, the files should show no differences. Save the changes simply by clicking on the "X" in the tab name.

![Merge complete](./images/mcp71.png?raw=true "Merge complete") 

6. Now you can run your server with the following command:

```
python mcp_server.py
```

7. Switch to another terminal and repeat the same process with the *mcp_client_agent.py* file. Review and merge in the changes, then save the changes by closing the tab at the top. Note in the code that tool names and model names and prompts are used as resources from the server, but LLM interaction is done in the client - as we would expect for a *real* agent.

```
cd ../lab4 
code -d ../extra/mcp_client_agent.txt mcp_client_agent.py
```
</br></br>
![Side-by-side merge](./images/mcp73.png?raw=true "Side-by-side merge")

8. Once you've completed the merge and closed the tab, run the client and select one of the commands and enter some text for it. For example you might select the "*expand*" command and then enter some basic text like "*MCP stands for Model Context Protocol*." After a few moments you should see some output from the client.

```
python mcp_client_agent.py
```

![Trying out the client](./images/mcp74-new.png?raw=true "Trying out the client")

9. (Optional) Start up the MCP inspector again and see the resources in the server. To do this, you'll need to start a new instance of the inspector. If the old one is running, you can close/stop it.  Then run the scripts/start_mcpi.sh script again to start a new instance.  (If you get a warning message from GitHub about connecting, just click *Continue*.) Then go to the URL it displays at the end and click *Connect*. After a few moments, it should connect to the server.

```
../scripts/start_mcpi.sh
```

![Starting the inspector](./images/mcp77-new.png?raw=true "Starting the inspector")

10. (Optional) If you did step 10, and got the server connected, you can click on the *Prompts* item in the top row and tell it to list the prompts. Due to some limitations, if you select *Get Prompts* you won't be able to see the full text of the prompt. You can also look at the resource with the model name, via the *Resources* option at the top. Finally, if you look at the *Tools* from the server, keep in mind that these are just wrappers around the prompts and won't actually change any text you enter.

![Running the inspector](./images/mcp75.png?raw=true "Running the inspector")

11. When done, you can stop the server via CTRL+C and the client via typing "exit" at a prompt. 


 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 5 - Connecting Applications to MCP Servers**

**Purpose: In this lab, we'll see how to connect GitHub Copilot to the GitHub MCP Server.**

1. For authentication to GitHub, we will need a GitHub personal access token (PAT). When logged into GitHub, click on the link below, provide a note and click the green "Generate token" button at the bottom.

Link:  Generate classic personal access token (repo & workflow scopes) https://github.com/settings/tokens/new?scopes=repo,workflow

![Creating token](./images/mcp10.png?raw=true "Creating token")

![Creating token](./images/mcp87.png?raw=true "Creating token")

<br><br>
   
2. On the next screen, make sure to copy the generated token and save it for use later in the lab. You will not be able to see the actual token again!

![Copying token](./images/mcp11.png?raw=true "Copying token")
<br><br>

3. If the Copilot Chat panel is not already open, then click on the Copilot icon at the top. And/or if it is  not already in Agent mode at the bottom (says "Ask" or "Edit" instead), switch to *Agent* mode  via the drop-down at the bottom. (**NOTE:** If you don't see *Ask* mode or an option to switch to another mode, you may need to complete a setup step as shown in the third screenshot below. Click on the Copilot icon in the bottom status bar and look for a button that says "*Finish setup*" and click on that. Then you should see the options.)

**Opening Chat if not open**

![Opening chat panel](./images/mcp69.png?raw=true "Opening chat panel")
<br>

**Completing setup - if needed**

![Completing setup](./images/mcp88.png?raw=true "Completing setup")
<br>

**Switching to Agent mode**

![Switching to Agent mode](./images/mcp12.png?raw=true "Switching to Agent mode")
<br><br>





4. Now we need to add the GitHub MCP Server configuration in our IDE. You could fill most of this out via IDE prompts, but for simplicity, we already have a sample configuration file that we can just copy in. Run the commands below in the terminal. The last one will open the file in the editor.

```
cd /workspaces/mcp
mkdir .vscode
cp extra/mcp_github_settings.json  .vscode/mcp.json
code .vscode/mcp.json
```

<br><br>

5. Now, we can start the local MCP server. In the *mcp.json* file, above the name of the server, click on the small *Start* link (see figure below). A dialog will pop up for you to paste in your PAT. Paste the token in there and hit *Enter*. (Note that the token will be masked out.)

![Starting the server](./images/mcp23.png?raw=true "Starting the server")

After this, you should see the text above the server name change to "√Running | Stop | Restart | ## tools | More...".

![Starting the server](./images/mcp24.png?raw=true "Starting the server")

<br><br>


6. To see the tools that are available, in the Copilot Chat dialog, click on the small *tool* icon (see figure) and then scroll down to the *MCP Server: GitHub MCP Server* section. You'll see the available tools we picked up under that.

![Viewing available tools](./images/mcp25.png?raw=true "Viewing available tools")

<br><br>


7. Now that we have these tools available, we can use them in Copilot's Chat interface. (Again, you must be in *Agent* mode.) Here are some example prompts to try:

```
Find username for <your name> on GitHub
Show info on recent changes in <repo path> on GitHub
```
</br></br>

8. Notice the mention of "Ran <tool name> - GitHub MCP Server (MCP Server) early in the output for each.

![Example usage](./images/mcp26.png?raw=true "Example usage")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Alternative approach to run inspector locally, if needed**

1. Clone down this repository

```
git clone https://github.com/skillrepos/mcp
```

2. If you are running in the codespace, in an available terminal, get the name of the codespace with the command below. Copy this to use in the next step.

```
echo https://${CODESPACE_NAME}-8000.app.github.dev/mcp
```

3. If you are not running in the codespace but running the server local, grab the URL for the host and port where the server is running - most likely something like *http://127.0.0.1:8000/mcp*

4. In your local clone, change to the mcp directory and run the command below (substituting in the value you copied in step 2 or 3 for SERVER_URL.

```
cd mcp
scripts/local_mcpi.sh SERVER_URL
```
5. This should eventually open up a browser with the inspector running in the tab on localhost:6274. (You may also see a failed browser open for the proxy port on 6277. You can ignore that.)

6. Click connect to connect to the server and continue with the lab.

7. If you still can't connect, make sure that the URL you copied in step 2 is in the URL area on the left and that the protocol is set to Streamable HTTP.

![Correct fields](./images/mcp91.png?raw=true "Correct fields")

<br><br>
**THE END**

