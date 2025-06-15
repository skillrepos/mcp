# Understanding MCP (Model Context Protocol) - A hands-on guide
## Understanding how AI agents can connect to the world
## Session labs 
## Revision 1.0 - 06/15/25

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

3. This created an index that is persisted in a *ChromaDB* database. Now we can run a simple search tool that will take whatever prompt/query we enter and return the primary match that it finds in the index of our codebase. Run the first command below. Then you can enter prompts like the next two lines. Type "exit" to quit.

```
python ../extra/search.py
Where does the code use authentication?
Is there already a module that implements our data store?
```

![Searching vector DB](./images/sdlc3.png?raw=true "Searching vector DB")

4. What you are seeing here is just the hits from searching the vector database that we created. To make this more useful, we would get these hits to an LLM by adding to the prompt to give it more specific context. We can see the end results of that by letting Copilot index our code in the codespace environment. Click on the Copilot icon at the bottom. If you see a blue button to Setup Copilot, go ahead and click on that. Then check the two checkboxes for "Code Completions (all files)" and "Code Completions (Python)".  After a few moments, if you click the icon again, you should see a line at the top of that dialog that says "Locally indexed". (There will also be a link next to it that says "Build remote index". That can be used to build an index on the GitHub side. We don't need to do that right now.)

![Copilot locally indexed](./images/sdlc4.png?raw=true "Copilot locally indexed")

5. With the local index in place, let's see how Copilot responds to a generic request. Go to the Copilot Chat interface (on the right) and type in the prompt below. (Note we are using the chat variable **#codebase** to tell Copilot to look at the complete set of code in our app.) 

```
Where in this #codebase do we enforce authentication?
```

7. Note that the answers that come back have the information, but are also more conversational in their response. (The answer may vary in format and text depending on several factors.)

![Copilot response to authentication](./images/sdlc5.png?raw=true "Copilot response to authentication")

8. We can also try our other example. Enter the prompt below. After running, you should see something like the screenshot below.
```
Is there a module in our #codebase that handles data storage?
```

![Copilot response to datastore](./images/sdlc6.png?raw=true "Copilot response to datastore")

9. Let's try one more query here. To demonstrate further how AI can help with planning, prompt Copilot with the prompt below (JWT = JSON Web Token):

```
What would it take to change #codebase to use JWT for authentication?
```

10. After this runs, you should see an answer in the chat screen similar to what's shown in the screenshot below. Notice that it includes not only text explanations, but also the changed code.

![Copilot response to JWT](./images/sdlc7.png?raw=true "Copilot response to JWT")


12. Finally, let's run our app and see it in action. To start it, run the command below in the terminal.

```
python app.py
```

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 2: Using AI during the development phase**

**Purpose: In this lab, we'll see how to use an AI assistant to help implement a feature request to our codebase.**

1. Let's try out the app. Start the app running in the terminal via the command below:

```
python app.py
```

2. Next, let's open a second terminal to use for sending commands to the app. Right-click in the terminal and select *Split Terminal* to get a second terminal next to the current one.

![Split terminal](./images/sdlc9.png?raw=true "Split terminal")

4. Our code is missing a *search* feature currently. Try the following command in the terminal.

```
# Search items:
curl -i \
  -H "Authorization: Bearer secret-token" \
  http://127.0.0.1:5000/items/search?q=milk
```

2. Notice that we get a 404 response and a message indicating that the URL was not found on the server.

3. In our repository, we already have a GitHub Issue for this feature. Take a look at it by clicking on this link: [GitHub Issue #1](https://github.com/skillrepos/ai-sdlc/issues/1)

4. In order to use this information as context for the AI, we'll add the text of the issue to the AI's prompt context. First, we need to get the text from the issue.
We have a script for this in our project. Run the command below to do this. (The "1" is the number of the GitHub Issue.)

```
./get-issue-info.sh 1
```

5. The output of running this file should be a new file in your project named FIX_ISSUE_1.md. You can click on it and open it up to view the contents.

![Displaying file](./images/sdlc11.png?raw=true "Displaying file")

6. In Copilot's Chat interface, change the mode to "Agent" by clicking on the drop-down labeled "Ask" at the bottom.

![Switch to Agent mode](./images/sdlc10.png?raw=true "Switch to Agent mode")

7. We now want to add this file as context for our prompt in the Chat panel. Click on the "Add context" item in the prompt area and select it from the list that pops up. (You may have to scroll down to find it.)

![Adding context](./images/sdlc13.png?raw=true "Adding context")

8. With the FIX_ISSUE_1.md file attached as context, enter the following prompt in the chat area and then submit it.

```
Here's the full text of GitHub Issue #1. Propose a diff to our Python codebase that implements the requested feature. Do not create or add any tests.
```
![Context and prompt](./images/sdlc15.png?raw=true "Context and prompt")

9. After Copilot processes the prompt, it should show two files changed - *app.py* and *datastore.py*. Click on the +- icon on the right of the "2 files changed" area in the dialog. (See figure below).  Take a look at the diffs. When you are satisfied with the proposed changes, click on the *Keep* button in the *Files changed* dialog.

![Reviewing changes](./images/sdlc17.png?raw=true "Reviewing changes")

10. After clicking on the "Keep" button, you can close the  "Suggested Edits (2 files)" tab if you want. Now, let's try the *search* operation again. In the terminal where you started the app running in Lab 1, kill the process (CTRL+C). Then run the app again.

```
python app.py
```

11. You can try the search operation with the same curl command as before. This time, it should run and return a 200 code rather than 404 since the search endpoint is implemented. If the item is found, it will return the found item. If not, it returns the empty set "[]".

```
# Search items:
curl -i \
  -H "Authorization: Bearer secret-token" \
  http://127.0.0.1:5000/items/search?q=milk
```

12. To show that the search function actually returns an item after adding, there is a script in the "scripts" directory named use-app.sh. You can open it up and look at it. It adds a new item, lists it, then does a search and delete. You can run it with the following command:

```
../scripts/use-app.sh
```
 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 3: Fixing bugs with AI**

**Purpose: In this lab, we'll see how to fix bugs with AI.**

1. Let's see what happens if we try to delete a non-existent item in our list. Run the command below.

```
# Delete an item:
curl -i \
  -X DELETE \
  -H "Authorization: Bearer secret-token" \
  http://127.0.0.1:5000/items/4
```

2. Notice that the attempt returns a 500 return code indicating *server error*. We'd rather have it return a 404 error indicating *Not found*.

![500 error](./images/sdlc18.png?raw=true "500 error")

3. Select/open the app.py file in the editor so it will be the current context. Then, so we have more control over changes, switch Copilot back to "Edit mode" by clicking on the drop-down at the bottom of the chat input dialog.

![Switch mode](./images/sdlc21.png?raw=true "Switch mode")

4. Now, let's let Copilot have a try at fixing this. Enter and submit the following prompt.

```
Fix the delete endpoint so that deleting a missing item returns 404 JSON {error: 'Not found'} instead of a server error.
```

![Fix delete](./images/sdlc22.png?raw=true "Fix delete")


5. After Copilot processes this, you should see a changed app.py file. Let's add Copilot as a reviewer to have it take a look. Go to the diff (green part) and right-click and select the menu item "Copilot" -> "Review and comment".

![Add Copilot review](./images/sdlc23.png?raw=true "Add Copilot review")

6. You'll then need to select a range for it to review. You can just tell it to review the entire delete function.

![Pick review range](./images/sdlc24.png?raw=true "Pick review range")

7. Copilot should review the proposed changes and offer any suggestions. For this case, it will probably not have any suggestions, so you can just select "OK". If it does have suggestions, you can choose to Accept/Keep or Discard/Undo them. If there were multiple changes, you would repeat this same process to have Copilot review all changes and Accept/Keep or Discard/Undo each one.

![Review output](./images/sdlc25.png?raw=true "Review output")

8. Once you are satisfied with the set of changes and reviews, go ahead and click one of the Keep buttons to save the changes.

![Keep](./images/sdlc26.png?raw=true "Keep")

10. Now, you can repeat step #1 and hopefully you'll see a 404 error "Not found" instead of a 500 one.

![Fixed code](./images/sdlc27.png?raw=true "Fixed code")

<p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 4: Testing**

**Purpose: In this lab, we'll see how to use AI to generate tests for our code.**

1. For this lab, we'll utilize Copilot's Agent functionality again. Change the mode from "Edit" to "Agent" as you've done before. If a dialog pops up about changing the chat, just answer "Yes".
   
2. We want Copilot to generate unit tests for our datastore code and integration tests for each of our endpoints. Enter the prompt below into chat.

```
Write pytest unit tests for DataStore (all CRUD + search) and Flask integration tests for each endpoint (including auth failure).
```

![Prompt for tests](./images/sdlc28.png?raw=true "Prompt for tests")

3. As this runs, if you encounter points where Copilot wants to run commands in the terminal and/or offers a "Continue" button, go ahead and accept that. If it simply notes commands and stops, go ahead and copy and paste those into the terminal and run them.

![Continue to execute command](./images/sdlc30.png?raw=true "Continue to execute command")

4. After the testing commands are run, you should hopefully see a clean run and the agent will notify you that things have completed successfully.

![Clean test run](./images/sdlc31.png?raw=true "Clean test run")
![Clean results](./images/sdlc32.png?raw=true "Clean results")

5. If you have any failing tests, you can try adding a prompt of "Tests do not run cleanly" and submit that to Copilot. Again, accept any attempts to run things in the terminal. Or, you can start a new Agent mode chat session by clicking the "+" sign in the upper left to start a new chat session and try the same prompt again.
   
6. You should now see test files for app integration tests and unit tests for the datastore pieces. Make sure to save your testing files with one of the *Keep* buttons.

![New test files to keep](./images/sdlc33.png?raw=true "New test files to keep")

7. Now, let's see how else AI can help us with testing by entering a prompt (in the Chat panel and still in "Agent" mode) asking what else to test. 

```
What else in the #codebase should we test? 
```
![What else](./images/sdlc34.png?raw=true "What else")

8. Copilot should suggest some other test cases and then ask if it should add them. You can tell it to add the most important ones with a prompt like the one below.

```
Yes, but just add the most important ones.
```

![Add most important](./images/sdlc35.png?raw=true "Add most important")

9. After this, it may also suggest a command in the terminal to run to verify the tests. If so, click on Continue.

![Add most important](./images/sdlc36.png?raw=true "Add most important")

11. If the command fails, it should suggest a fix. If so, you can accept that and then complete the cycle. Save files with any changes.

![Add most important](./images/sdlc38.png?raw=true "Add most important")   

12. (Optional) If you have time and want, you can prompt the AI with other prompts for other testing, such as the following:

```
What edge cases in #codebase should I test?
How do I test for performance in #codebase?
How do I test for security in #codebase?
```

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 5: Refactoring**

**Purpose: In this lab, we'll see how to use the AI to refactor our code, both for efficiency and improvements.**

1.  Change Copilot's mode back to "Ask".

![Change to Ask](./images/sdlc39.png?raw=true "Change to Ask")

2. Let's ask Copilot how we can refactor our code to be more efficient. Enter the prompt below.

```
How can we factor #codebase to make our code more efficient?
```

3. After this runs, you will likely see output like the screenshot.

![Refactor suggestions](./images/sdlc40.png?raw=true "Refactor suggestions")

4. Below that, you should also have some suggested code changes. Hover over the code in the Chat window and a set of controls will pop up. Click on the leftmost one to apply the differences.

![Apply refactor suggestions](./images/sdlc41.png?raw=true "Apply refactor suggestions")

5. We're going to add Copilot as a reviewer. In order to see how it reacts to an error, let's introduce one. In one of the green sections where a change is being added, edit the code and change an instance of "None" to "one".

![Introduce error](./images/sdlc42.png?raw=true "Introduce error")

6. Now, add Copilot as a reviewer. Highlight all the code, then right-click and select "Copilot"->"Review and Comment" from the menu.

![Add Copilot as reviewer](./images/sdlc43.png?raw=true "Add Copilot as reviewer")

7. After this runs, Copilot should catch the issue and add its comment. You can review its suggestion, then just click "Apply and Go to Next". After this, if there are other suggestions from Copilot, you can work your way through them deciding whether to apply them or not. *Make sure to Keep/Save changes when done.*
![Working through reviews](./images/sdlc44.png?raw=true "Working through reviews")
   
8. Now, let's look at how to use Copilot to add another feature. Switch the chat mode to "Edit" by clicking on the drop-down at the bottom of the chat dialog. Then use the "Add Context" control to select our *datastore.py* and *app.py* files as context (if not already added). (You may need to click on "Files and Folders" in the context picker dialog.)

![Add context](./images/sdlc45.png?raw=true "Add context")

9. Let's add logging to our functions. In the prompt area, add the prompt "Add logging for all endpoints". When ready, click Submit.

![Logging prompt](./images/sdlc46.png?raw=true "Logging prompt")

10. After this runs, you should see changes in *app.py*. There may also be review comments by Copilot. Navigate through them and Apply/Keep changes as warranted.

![Logging changes made](./images/sdlc47.png?raw=true "Logging changes made")

11. (Optional) To show that the logging works, you can use the script we used previously in the "scripts" directory named use-app.sh. Running it now should cause INFO messages to be output to stderr. (Don't forget to make sure the app is running first.)

```
../scripts/use-app.sh
```

![Logging events](./images/sdlc48.png?raw=true "Logging events")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 6: Documentation**

**Purpose: In this lab, we'll see how to use AI to quickly and easily create different kinds of documentation for our project.**

1. Let's start out by telling our AI to generate basic doc. Open the inline chat via Ctrl+I or Option+I and enter the following shortcut command:

```
/doc
```

![doc command](./images/sdlc49.png?raw=true "doc command")


2. Notice after this, that only the function/method headers have comments.

![doc results](./images/sdlc50.png?raw=true "doc results")

3. To get comments in the body of the code, we need to further prompt the AI. Let's tell Copilot to verbosely comment the code. Enter the prompt below in Copilot. You can also choose to change the model that's being used. Some of these will be higher cost than others. *Claude 3.7 Sonnet* should be the same cost.

```
Verbosely comment all code so it is easy to follow and understand
```

![verbose and change model](./images/sdlc51.png?raw=true "verbose and change model")

4. In the main chat window, switch the mode back to "Ask". Also, open a new chat window using the "+" control again in the top right.

5. Now, in the main chat window, enter the prompt below:

```
Generate Sphinx-style .rst API documentation for this Flask service
```

![generate Sphinx-style doc](./images/sdlc52.png?raw=true "Generate Sphinx-style doc")

6. Let's try another example. Let's have the AI generate functional documentation that we can share with others. Use the prompt below for this:

```
Generate functional documentation for all API endpoints
```

![Generate functional doc](./images/sdlc53.png?raw=true "Generate functional doc")

7. After the documentation is generated, you can hover over the output and insert it into a new file if you want. If you then save the file with a .md extension, you'll be able to see the document in Markdown format. (You can use the three-bar menu, in the upper left of the codespace, then select "File", then "Save As...".)


![Save functional doc](./images/sdlc54.png?raw=true "Save functional doc")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**Lab 7: Onboarding/Explaining code**

**Purpose: To show how AI can be used to explain code and also help with onboarding those new to a codebase.**

1. Switch back to Agent mode for this lab. (If you do it in Ask mode, it will try to answer for all the different types of files in the project, rather than just the "app" code.

2. Let's start out having Copilot explain the code to us. Enter the prompt below in one of the chat interfaces.
```
Explain in simple terms how this code works
```

![Explain code](./images/sdlc55.png?raw=true "Explain code")


3. Someone just starting out with this code would need to also know how to run it, so let's have the AI explain how to do that as well.
```
Provide examples of how to run this code
```

![How to run](./images/sdlc56.png?raw=true "How to run")

4. Let's also use the AI to try and anticipate any potential issues new users may run into. Here's a prompt for that.
```
What are the most likely problems someone new to this codebase would run into. Explain the issue clearly and succinctly.
```

![Most likely problems](./images/sdlc57.png?raw=true "Most likely problems")

5. Let's take this a step further and have the AI create a general guide for new users to the code. You can use the prompt below. When done, you can hover over the code block and insert into a new file and then save as a .md file to see the formatting.
   
```
Create an onboarding guide for anyone brand new to this code who will be working with it or maintaining it.
```

![Onboarding guide](./images/sdlc58.png?raw=true "Onboarding guide")

6. Finally, let's have the AI generate some basic Q&A to check understanding and learning for someone looking at the code. Try this prompt:
```
Construct 10 questions to check understanding of how the code works. Then prompt the user on each question and check the answer. If the answer is correct, provide positive feedback. If the answer is not correct, explain why and provide the correct answer.
```

![Checking for understanding](./images/sdlc59.png?raw=true "Checking for understanding")

 <p align="center">
**[END OF LAB]**
</p>
</br></br></br>

**THE END**
