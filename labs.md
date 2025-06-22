# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 1.2 - 06/22/25

**Versions of dialogs, buttons, etc. shown in screenshots may differ from current version used in dev environments**

**Follow the startup instructions in the README.md file IF NOT ALREADY DONE!**

**NOTES:**
1. We will be working in the public GitHub.com, not a private instance.
2. Chrome may work better than Firefox for some tasks.
3. Substitute the appropriate key combinations for your operating system where needed.
4. The default environment will be a GitHub Codespace (with Copilot already installed). If you prefer to use your own IDE, you are responsible for installing Copilot in it. Some things in the lab may be different if you use your own environment.
5. To copy and paste in the codespace, you may need to use keyboard commands - CTRL-C and CTRL-V.**
6. VPNs may interfere with the ability to run the codespace. It is recommended to not use a VPN if you run into problems.
</br></br></br>

**Lab 1 - MCP Lightning Lab: From Hand-Rolled API Calls to Zero-Boilerplate Tool Invocation**

**Purpose: In this lab, we'll contrast the traditional approach of hard-coding REST requests against the Model-Context Protocol (MCP) approach to automatically discover, validate, and invoke tools—then see how an LLM can seamlessly leverage those same MCP-exposed functions without any extra HTTP or JSON glue code.**

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


3. Now, run the code using the command below. You should see the expected answer (96) printed out. Notice that you needed to know the endpoint, URL-encode the call, and parse the response yourself. This is only for one tool, but imagine doing this for multiple tools.

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
code mpc_client.py
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
![Running client](./images/mcp7.png?raw=true "Running client")

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

2. In this directory, we have an example MCP server with tools, a prompt, and a resource.  It's designed as a "travel assistant" example. Open the file and take a look at the code. The numbered comments highlight the key parts.

```
code mcp_travel_server.py
```

3. Before we run it, let's grab a unique URL to more easily run the inspector. In the terminal, run the command below, and copy the URL after "Inspector URL=" that's shown.

```
../scripts/get-inspector-url.sh
```
</br></br>
![Copy URL](./images/mcp35.png?raw=true "Copy URL")


4. Now, let's start the server running. Issue the command below in the terminal. You should see the code start up and say it is running on localhost (127.0.0.1) and availale on port 8000.

```
python mcp_travel_server.py
```
</br></br>
![Running server](./images/mcp36.png?raw=true "Running server")


5. Before we can connect everything, we need to make a couple of ports *Public* that are exposed by the server and client. To do this, switch to the *PORTS* that is next to the *TERMINAL* tab. Then find the rows for the port 8000 (used by the server) and port 6477 (used by the inspector). On each of these rows, right-click and select the menu item for *Port visibility*. Then set the visibility for both ports to *Public*.

![Setting ports to Public](./images/mcp31.png?raw=true "Setting ports to Public")


6. After this, you can go to a new browser tab and paste the URL you copied in step 3 into a browser tab. You should see the MCP Inspector displayed. **Click on the Connect button** to connect to the server.

![Connecting](./images/mcp34.png?raw=true "Connecting")
   
7. If all goes well, you'll now be connected to the server. Now you can start exploring the various items the server makes available. First, let's look at the *Resources*. As shown in the screenshot, click on *Resources* in the top gray bar, then click on *List Resources*. This should show a resource named *major_cities*. Click on that and you should see a display of the actual resource as defined in the server we started earlier.

![Resources](./images/mcp27.png?raw=true "Resources") 

8. Next up, you can take a look at the prompt from the server. In the gray bar at the top of the inspector, click on *Prompts*, then *List Prompts* in the box below. You should see a prompt with the name of "recommend_sightseeing" listed. Click on that item and then you should see an item for that displayed to the right. In the box on the right, click on "Get Prompt" and you'll see the actual definition of the prompt.

![Prompt](./images/mcp28.png?raw=true "Prompt") 

9. Finally, let's take a look at the tools available from the server. Click on *Tools* in the gray bar, then *List Tools* in the box below. You'll see two tools defined - one to calculate distance and one to convert currency.

![Tools](./images/mcp37.png?raw=true "Tools") 

10. Let's try running the distance_between tool. Select the tool in the list. On the right side, you'll see the input fields for the tool. You can try any latitude and longitude values you want and then click "Run Tool" to see the results. (The example used in the screeshot - 40,74 and 51, .12 - equates roughly to New York and London.)

![Running tool](./images/mcp37.png?raw=true "Running tool") 

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

11. In preparation for other labs, you can stop (CTRL+C) the running instance of mcp_travel_server.py in your terminal to free up port 8000.

**Lab 3 - MCP Lightning Lab: From Hand-Rolled API Calls to Zero-Boilerplate Tool Invocation**

**Purpose: In this lab, we'll contrast the traditional approach of hard-coding REST requests against the Model-Context Protocol (MCP) approach to automatically discover, validate, and invoke tools—then see how an LLM can seamlessly leverage those same MCP-exposed functions without any extra HTTP or JSON glue code.**

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

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 4 - MCP Lightning Lab: From Hand-Rolled API Calls to Zero-Boilerplate Tool Invocation**

**Purpose: In this lab, we'll contrast the traditional approach of hard-coding REST requests against the Model-Context Protocol (MCP) approach to automatically discover, validate, and invoke tools—then see how an LLM can seamlessly leverage those same MCP-exposed functions without any extra HTTP or JSON glue code.**

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

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 5 - MCP Lightning Lab: From Hand-Rolled API Calls to Zero-Boilerplate Tool Invocation**

**Purpose: In this lab, we'll contrast the traditional approach of hard-coding REST requests against the Model-Context Protocol (MCP) approach to automatically discover, validate, and invoke tools—then see how an LLM can seamlessly leverage those same MCP-exposed functions without any extra HTTP or JSON glue code.**

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

3. If not already in Agent mode, switch to *Agent* mode in the Copilot Chat panel via the drop-down at the bottom.

![Switching to Agent mode](./images/mcp12.png?raw=true "Switching to Agent mode")

4. Now we need to add the GitHub MCP Server configuration in our IDE. Start by pressing
 F1 to bring up the *Command Palette* and in the text area, type "mcp: add server" and press *Enter*.

![Add MCP server item](./images/mcp13.png?raw=true "Add MCP server item")

5. Select *HTTP (HTTP or Server-Sent Events)* as the type of MCP server to add.

![Choose server type](./images/mcp14.png?raw=true "Choose server type")

6. Enter the *Server URL*. You can copy it from the text below or type it in *carefully*.

```
https://api.github.com/mcp/
```
</br></br>

![Enter server URL](./images/mcp15.png?raw=true "Enter server URL")

7. Choose a *Server ID*. This is simply a name to refer to the MCP Server by. You can use the default or type in a more descriptive one as shown in the image.

```
GitHub MCP Server
```
</br></br>

![Enter Server ID](./images/mcp16.png?raw=true "Enter Server ID")

8. Choose where to save the configuration. Select the *Workspace Settings* option. This will create a *.vscode/mcp.json* settings file in your workspace.

![Save configuration](./images/mcp21.png?raw=true "Save configuration")

9. Now, we need to update the mcp.json file to authenticate and grab your personal access token (PAT) when it starts up. You can either replace the text in the current file with the text below or you can grab the text from the file *extra/mcp_github_settings.json*. After updating the file, it should look like the screenshot.

```
{
    "servers": {
      "GitHub": {
        "type": "http",
        "url": "https://api.githubcopilot.com/mcp/",
        "headers": {
          "Authorization": "Bearer ${input:github_token}"
        }
      }
    },
    "inputs": [
      {
        "id": "github_token",
        "type": "promptString",
        "description": "GitHub Personal Access Token",
        "password": true
      }
    ]
}
```
</br></br>

![Updated configuration](./images/mcp22.png?raw=true "Updated configuration")

10. Now, we can start the local MCP server. In the *mcp.json* file, above the name of the server, click on the small *Start* link (see figure below). A dialog will pop up for you to paste in your PAT. Paste the token in there and hit *Enter*. (Note that the token will be masked out.)

![Starting the server](./images/mcp23.png?raw=true "Starting the server")

After this, you should see the text above the server name change to "√Running | Stop | Restart | 51 tools | More...".

![Starting the server](./images/mcp24.png?raw=true "Starting the server")

11. To see the tools that are available, in the Copilot Chat dialog, click on the small *tool* icon (see figure) and then scroll down to the *MCP Server: GitHub MCP Server* section. You'll see the available tools we picked up under that.

![Starting the server](./images/mcp25.png?raw=true "Starting the server")

12. Now that we have these tools available, we can use them in Copilot's Chat interface. (Again, you must be in *Agent* mode.) Here are some example prompts to try:

```
Find username for <your name> on GitHub
Show info on recent changes in skillrepos/mcp on GitHub
```
</br></br>
![Example usage](./images/mcp26.png?raw=true "Example usage")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**THE END**
