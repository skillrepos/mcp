# Understanding MCP
## Repository for Understanding MCP (Model Context Protocol) - A hands-on guide 

These instructions will guide you through configuring a GitHub Codespaces environment that you can use to run the code.

Prefer to run the labs on your own machine instead? See **[LOCAL_SETUP.md](./LOCAL_SETUP.md)**
for the full list of prerequisites and setup steps. The Codespace is the environment the labs
are verified against, so a few things will look different locally.

> **Updated for MCP specification revision `2026-07-28`.** This is a breaking protocol
> change: the `initialize` handshake and `Mcp-Session-Id` are gone, servers can no longer
> push requests to clients, and Roots, Sampling and Logging are deprecated. See the
> "Parts of 2026-07-28 we did not lab" appendix at the end of `labs.md`, and
> `MCP-2026-07-28-UPDATE-REPORT.md` for the full rundown.
>
> The labs run on **FastMCP 4**, pinned exactly in `requirements.txt` (currently
> 4.0.3, the stable release line - FastMCP 4.0 went stable on 2026-08-31).
> FastMCP 3.4.x hard-pins `mcp<2.0` and cannot speak this protocol revision.

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


