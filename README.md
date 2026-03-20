# Understanding MCP
## Repository for Understanding MCP (Model Context Protocol) - A hands-on guide 

These instructions will guide you through configuring a GitHub Codespaces environment that you can use to run the code. 

<br><br>

**1. Set a longer timeout for the environment we'll be using - GitHub Codespaces.**

When logged into GitHub, go to [https://github.com/settings/codespaces](https://github.com/settings/codespaces).

Scroll down and find the *Default idle timeout* section and set it to at least 60 minutes.

![Extending timeout](./images/mcp99.png?raw=true "Extending timeout")

<br><br>

**2. Click on the button below to start a new codespace from this repository.**

Click here ➡️  [![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/skillrepos/mcp?quickstart=1)

<br><br>

**3. Then click on the option to create a new codespace.**

![Creating new codespace from button](./images/mcp1.png?raw=true "Creating new codespace from button")

This will run for a few minutes while it gets the virtual environment ready. You'll then need to run a setup script to finalize the installation.

<br><br>

**4. Run the warmup script in the TERMINAL to make the LLM interactions faster.**

```
python scripts/warmup.py &
```

![warmup](./images/aia2b3.png?raw=true "warmup")

<br><br>

**5. Open the labs file.**

You can open the [labs.md](./labs.md) file either in your codespace or in a separate browswer tab/instance.**

![Labs](./images/mcp78.png?raw=true "Labs")


