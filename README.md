# Understanding MCP
## Repository for Understanding MCP (Model Context Protocol) - A hands-on guide 

These instructions will guide you through configuring a GitHub Codespaces environment that you can use to run the code.

> **Updated for MCP specification revision `2026-07-28`.** This is a breaking protocol
> change: the `initialize` handshake and `Mcp-Session-Id` are gone, servers can no longer
> push requests to clients, and Roots, Sampling and Logging are deprecated. See the
> "What changed" section at the top of `labs.md`, and `MCP-2026-07-28-UPDATE-REPORT.md`
> for the full rundown.
>
> The labs run on **FastMCP 4.0.0b1**, which is a beta and is pinned exactly in
> `requirements.txt`. FastMCP 3.4.x cannot speak this protocol revision. 

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

This will run for a few minutes while it gets the virtual environment ready. When the main portion is done, it will still need to do some post-processing. That will look like this:

![Post-processing](./images/mcp117.png?raw=true "post-processing")

It will be done when you see output similar to this in the terminal.

![Ready](./images/mcp116.png?raw=true "ready")


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


