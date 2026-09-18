# Local Development Setup for MCP Labs

This guide sets up the MCP (Model Context Protocol) lab environment on your own machine,
replicating what the GitHub Codespace provides. The Codespace is the default and supported
environment (see `README.md`); if you use your own machine, you are responsible for the
installs below, and some screenshots in `labs.md` will differ.

Everything here is derived from what the labs actually run: `.devcontainer/devcontainer.json`,
`.devcontainer/Dockerfile`, `requirements.txt`, and the setup scripts in `scripts/`.

## 🖥️ System Requirements

Matching the devcontainer's `hostRequirements`:

- **CPU**: 4+ cores (the labs run an LLM locally on CPU)
- **RAM**: 16GB+
- **Storage**: 32GB+ available
- **OS**: macOS, Linux, or Windows with WSL2 (run all lab commands inside WSL2)

## 📋 Prerequisites

### 1. Python 3.11+

The stack pins FastMCP 4 / MCP SDK 2 / pydantic 2.12+, which need a modern Python. The
devcontainer image is Debian bookworm (Python 3.11).

```bash
# Check your version
python3 --version

# macOS with Homebrew
brew install python@3.11

# Ubuntu/Debian
sudo apt update && sudo apt install python3 python3-pip python3-venv

# Windows: use WSL2 and follow the Ubuntu instructions
```

### 2. Node.js 18+ (LTS)

Needed for **Lab 1 step 5**, which runs the prebuilt calculator MCP server over `npx`:
`npx -y github:skillrepos/calculator-mcp --port 8931`

```bash
# Check your version
node --version
npm --version

# macOS with Homebrew
brew install node

# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows: https://nodejs.org/ (or install inside WSL2)
```

### 3. Ollama + llama3.2

The Lab 1 and Lab 3 agents call a **local** model through Ollama's HTTP API at
`http://127.0.0.1:11434` — no hosted API key is involved. The model name is pinned to
`llama3.2` in `lab1/agent_helpers.py` and `lab3/ask_agent.py`.

Installed and pulled for you by `scripts/startOllama.sh` in Step 5 below; you can also
install it yourself from https://ollama.com/download.

### 4. VS Code with the `code` command on your PATH

Every lab opens files with `code <file>`, and Labs 1-4 complete skeleton files with the
side-by-side diff `code -d <finished> <starter>`. Lab 4 Part B additionally needs
**GitHub Copilot Chat** in *Agent* mode, driven from `.vscode/mcp.json`.

On macOS, if `code` isn't found: open VS Code, Command Palette (CMD+SHIFT+P) →
*Shell Command: Install 'code' command in PATH*.

### 5. curl, jq, and git

Lab 5 requests tokens from the authorization server with `curl` and pulls them out of the JSON with `jq`.

```bash
# macOS
brew install curl jq git

# Ubuntu/Debian
sudo apt install -y curl jq git
```

## 🚀 Environment Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/skillrepos/mcp
cd mcp
```

All lab paths in `labs.md` are relative to this directory. Where the labs say
`cd /workspaces/mcp` (Lab 4 step 5), use the path to this clone instead.

### Step 2: Set Up Python Environment

The labs expect an environment named `py_env` that is **already active** in every terminal —
lab commands say `python`, not `python3`.

```bash
# Create a virtual environment
python3 -m venv py_env

# Activate the environment
source py_env/bin/activate       # macOS/Linux/WSL2
# OR
py_env\Scripts\activate          # Windows PowerShell (labs assume WSL2)

# Auto-activate in new terminals, as the Codespace does (optional)
echo "source $(pwd)/py_env/bin/activate" >> ~/.bashrc   # Bash
echo "source $(pwd)/py_env/bin/activate" >> ~/.zshrc    # Zsh
```

### Step 3: Install Python Dependencies

`requirements.txt` is the single source of truth for pins — don't install by hand.

```bash
# Ensure virtual environment is activated
source py_env/bin/activate

pip install --upgrade pip setuptools wheel

# Linux only: install CPU-only PyTorch FIRST so pip doesn't pull ~3GB of CUDA
# wheels. (On macOS the default wheels are already CPU-only; skip this line.)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install everything the labs pin
pip install -r requirements.txt

# Sanity check
python -c "import fastmcp, mcp; print('fastmcp', fastmcp.__version__)"
```

Two things worth knowing about those pins (both explained in `requirements.txt`):

- **FastMCP 4 is required.** The 2026-07-28 protocol revision landed in MCP Python SDK
  v2 and the FastMCP 4.0 line. FastMCP 3.4.x hard-pins `mcp<2.0` and tops out at
  2025-11-25, so it cannot speak this revision. `fastmcp` on PyPI is a metadata wrapper
  around `fastmcp-slim`, which is why both are pinned to the same version.
- **`langchain_mcp_adapters` is deliberately absent.** It imports `mcp.server.fastmcp`,
  a module deleted in SDK v2. Lab 1's agent drives the tool-calling loop directly instead.

### Step 4: Install the Merge Info VS Code Extension

This is what produces the **yellow bands** in skeleton files and the **hover notes** in the
diff views, both described near the top of `labs.md`. The Codespace installs it
automatically; locally you install it once:

```bash
code --install-extension .devcontainer/merge-info-0.3.1.vsix --force
```

Then enable the two settings the devcontainer sets (Settings JSON, or Settings UI →
search "merge info"):

```json
{
  "mergeInfo.skeletonHighlights": true,
  "mergeInfo.reviewHighlights": true
}
```

To toggle the bands off mid-lab: Command Palette → *Merge Info: Toggle Skeleton Highlights*.

The annotations come from `merge-info.json` in the repo root. The labs still work without
the extension — you just lose the bands and notes.

### Step 5: Set Up and Warm Ollama

Use the repo's own scripts, which are what the Codespace runs:

```bash
# One-time: install Ollama if needed and pull llama3.2 (a few minutes)
bash scripts/startOllama.sh

# Every time you start work: serve the model and warm it into RAM
bash scripts/serveOllama.sh

# Verify
ollama list
curl -s http://localhost:11434/api/tags
```

`serveOllama.sh` matters for two reasons the labs depend on:

- It starts the server with `OLLAMA_KEEP_ALIVE=-1`. Ollama's default unloads a model
  5 minutes after last use, and students spend well over 5 minutes on Lab 1 steps 1-10 —
  without this the model is cold again by step 11.
- It makes one real inference call. `ollama pull` only writes weights to disk; nothing is
  resident until something generates.

If you start Ollama yourself instead: `OLLAMA_KEEP_ALIVE=-1 ollama serve &`.

## 🔌 Ports the Labs Use

Make sure these are free (note: the labs use the repo's own **MCP Explorer**, not the
`@modelcontextprotocol/inspector` package, so nothing listens on 6274/6277):

| Port | Used by |
|---|---|
| **8000** | Every lab server: `note_server.py`, `helpdesk_server.py`, `poisoned_server.py`, `gateway.py`, `secure_server.py`. Only one at a time — stop the previous one with CTRL+C |
| **8931** | Lab 1's prebuilt calculator MCP server (`npx github:skillrepos/calculator-mcp`) |
| **5000** | Lab 2's MCP Explorer web UI (`scripts/mcp_explorer.py`) |
| **9000** | Lab 5's authorization server (`auth_server.py`) |
| **11434** | Ollama |

## 🗂️ Project Structure

```
mcp/
├── py_env/                     # Python virtual environment (symlinked in the Codespace)
├── lab1/                       # Lab 1 - MCP Jumpstart
│   ├── agent_mcp.py            # Minimal MCP agent (diff-and-merge skeleton)
│   └── agent_helpers.py        # Ollama + trace plumbing, provided complete
│                               # (classic_calc.py and mcp_client.py you create in the lab)
├── lab2/                       # Lab 2 - Building MCP Servers
│   ├── note_server.py          # Note-taking server (diff-and-merge skeleton)
│   └── wire_probe.sh           # Raw-HTTP tour of the protocol (kept, not a lab step)
├── lab3/                       # Lab 3 - Designing Tools an AI Can Use
│   ├── helpdesk_server.py      # Under-described server (diff-and-merge skeleton)
│   ├── show_tools.py           # Prints what the model is told; --scan checks it
│   ├── ask_agent.py            # The Lab 1 agent, provided complete
│   └── poisoned_server.py      # Same tools, one hostile description
├── lab4/                       # Lab 4 - MCP in the Real World
│   ├── math_server.py          # Second server to compose (skeleton)
│   └── gateway.py              # Mounts both servers behind one endpoint (skeleton)
├── lab5/                       # Lab 5 - Security and Authorization
│   ├── auth_server.py          # Authorization server (port 9000) - mints tokens
│   ├── secure_server.py        # Token-checking MCP server (signature, issuer, audience, expiry, scope)
│   ├── call_tool.py            # One tools/call request with a given token
│   ├── show_token.py           # Decodes a JWT's header and claims
│   └── secure_client.py        # Walks the discovery chain automatically
├── extra/                      # Completed code for diff-and-merge, plus retired labs
│   ├── agent_mcp.txt           # Lab 1 merge source
│   ├── note_server.txt         # Lab 2 merge source
│   ├── helpdesk_server.txt     # Lab 3 merge source
│   ├── math_server.txt         # Lab 4 merge sources
│   ├── gateway.txt
│   ├── mcp_local_settings.json # Copied to .vscode/mcp.json in Lab 4
│   ├── mrtr/                   # Retired: Multi Round-Trip Requests / elicitation
│   └── replicas/               # Retired: statelessness across replicas
├── scripts/
│   ├── pysetup.sh              # Python env setup (postCreate in the Codespace)
│   ├── startOllama.sh          # Install Ollama + pull llama3.2 (once)
│   ├── serveOllama.sh          # Serve + keep-alive + warm the model (each start)
│   ├── mcp_explorer.py         # The MCP Explorer used in Lab 2
│   └── warmup.py               # Optional extra warm-up pass (see note below)
├── .devcontainer/              # Codespace definition + Merge Info .vsix
├── merge-info.json             # Yellow-band / hover-note annotations
├── images/                     # Lab screenshots
├── requirements.txt            # Python dependencies (the pins)
├── labs.md                     # The labs
└── LOCAL_SETUP.md              # This file
```

> `scripts/warmup.py` is optional — `serveOllama.sh` already warms the model the labs
> use. It is still handy after a long idle gap, or on a local setup where you started
> Ollama yourself: `python scripts/warmup.py`.

## 🔧 Development Workflows

### Start-of-session checklist

```bash
cd /path/to/mcp
source py_env/bin/activate
bash scripts/serveOllama.sh
```

### Running the labs locally

```bash
# Lab 1 - calculator server on 8931, then the client and agent in a second terminal
npx -y github:skillrepos/calculator-mcp --port 8931
cd lab1 && python mcp_client.py && python agent_mcp.py

# Lab 2 - the note server, then the Explorer from the repo root
cd lab2 && python note_server.py
python scripts/mcp_explorer.py http://localhost:8000/mcp 5000   # then open http://localhost:5000

# Lab 3 - the help desk server, then show_tools and the agent in a second terminal
cd lab3 && python helpdesk_server.py
cd lab3 && python show_tools.py          # add --scan for the description checker
cd lab3 && python ask_agent.py

# Lab 4 - the gateway (needs lab2/note_server.py copied in, per the lab)
cd lab4 && python gateway.py

# Lab 5 - auth server, secure server, and client in three terminals
cd lab5 && python auth_server.py
cd lab5 && python secure_server.py
cd lab5 && python secure_client.py
```

The skeleton servers (`note_server.py`, `math_server.py`, `gateway.py`, `helpdesk_server.py`,
`agent_mcp.py`) **will not run until you merge in the completed code** with the lab's
`code -d ../extra/<name>.txt <name>.py` step. That is by design.

### Lab 4 Part B - Copilot Chat

Lab 4 step 5 creates the IDE config. From the repo root (the labs say `/workspaces/mcp`;
use your clone path):

```bash
mkdir -p .vscode
cp extra/mcp_local_settings.json .vscode/mcp.json
code .vscode/mcp.json
```

Then open Copilot Chat, switch it to *Agent* mode, and click *Start* above the
"Lab Gateway" entry in `mcp.json`. You need a signed-in GitHub Copilot subscription for
this part; the rest of the course does not use Copilot.

### Common tasks

- **Update dependencies**: `pip install --upgrade -r requirements.txt`
- **Reset the Python environment**: delete `py_env/` and repeat Steps 2-3
- **Reset a lab file you overwrote**: `git checkout <filename>`

## 🐛 Troubleshooting

### Python issues

```bash
# If virtual environment activation fails
python3 -m venv --clear py_env
source py_env/bin/activate

# Confirm you're on the venv's interpreter, not the system one
which python
python -c "import fastmcp; print(fastmcp.__version__)"   # expect 4.x
```

`ImportError: cannot import name 'Client' from 'fastmcp'` means a half-removed FastMCP 3
is shadowing 4.x. Fix it the way `scripts/pysetup.sh` does — uninstall both dists first,
then reinstall:

```bash
pip uninstall -y fastmcp fastmcp-slim
pip install -r requirements.txt
```

### Ollama issues

```bash
# Is it up and is the model there?
curl -s http://localhost:11434/api/tags
ollama list | grep llama3.2

# Model missing
ollama pull llama3.2
```

Slow agent runs in Lab 1 step 11 and Lab 3 are expected on CPU — a minute or two across
the loop's turns. If a tool result comes back as `NaN` or an argument is missing, run it
again; llama3.2 is small and occasionally drops an argument from a tool call. The labs say
so too.

### Lab 1 `npx` issues

The calculator server is fetched from GitHub on first use, so the first run takes 30-90s
while it clones and builds. If it exits immediately:

```bash
npm cache clean --force
npx -y github:skillrepos/calculator-mcp --port 8931
```

### Port conflicts

```bash
kill -9 $(lsof -t -i:8000) 2>/dev/null || true    # lab servers
kill -9 $(lsof -t -i:8931) 2>/dev/null || true    # lab 1 calculator
kill -9 $(lsof -t -i:5000) 2>/dev/null || true    # MCP Explorer
kill -9 $(lsof -t -i:9000) 2>/dev/null || true    # lab 5 auth server
```

On macOS, port 5000 is often taken by AirPlay Receiver (System Settings → General →
AirDrop & Handoff). Turn it off, or pass a different port to the Explorer:
`python scripts/mcp_explorer.py http://localhost:8000/mcp 5050`.

### Protocol version surprises

Lab 1's third-party calculator server negotiates `2025-11-25`, not `2026-07-28`. That is
expected and the lab calls it out — your client asks for the new revision and falls back.
Our own servers (Labs 2-5) answer `2026-07-28`.

## 📚 Additional Resources

- **MCP Specification (2026-07-28)**: https://modelcontextprotocol.io/specification/2026-07-28/
- **MCP Documentation**: https://modelcontextprotocol.io/
- **FastMCP Documentation**: https://gofastmcp.com (see the "Upgrading from FastMCP 3" guide)
- **Ollama**: https://ollama.com/download
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html
- **This course's change notes**: `MCP-2026-07-28-UPDATE-REPORT.md` and the `CHANGELOG-*.md` files

## 🎯 Quick Start Commands

```bash
git clone https://github.com/skillrepos/mcp
cd mcp
python3 -m venv py_env
source py_env/bin/activate
pip install --upgrade pip setuptools wheel
pip install -r requirements.txt
code --install-extension .devcontainer/merge-info-0.3.1.vsix --force
bash scripts/startOllama.sh      # once
bash scripts/serveOllama.sh      # each session
```

Then open `labs.md` and start with Lab 1.

## 🆘 Getting Help

1. **Check the troubleshooting section above**
2. **Verify the prerequisites** — especially Python 3.11+, the `code` CLI, and `jq`
3. **Confirm Ollama is serving and warm**: `curl -s http://localhost:11434/api/tags`
4. **Check that ports 8000, 8931, 5000, 9000 and 11434 are free**
5. **If something behaves differently than `labs.md` describes**, fall back to the
   GitHub Codespace — it is the environment the labs are verified against
