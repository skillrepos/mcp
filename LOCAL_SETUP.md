# Local Development Setup for MCP Labs

This guide helps you set up the MCP (Model Context Protocol) development environment on your local machine, replicating what's provided in the GitHub Codespace.

## 🖥️ System Requirements

Based on the devcontainer configuration, your system should have:

- **CPU**: 4+ cores recommended
- **RAM**: 16GB+ recommended  
- **Storage**: 32GB+ available space
- **OS**: macOS, Linux, or Windows with WSL2

## 📋 Prerequisites

### Required Software

1. **Python 3.8+**
   ```bash
   # Check your version
   python3 --version
   
   # Install on macOS with Homebrew
   brew install python
   
   # Install on Ubuntu/Debian
   sudo apt update && sudo apt install python3 python3-pip python3-venv
   
   # Install on Windows (use WSL2 or download from python.org)
   ```

2. **Node.js 18+ (LTS)**
   ```bash
   # Check your version
   node --version
   npm --version
   
   # Install on macOS with Homebrew
   brew install node
   
   # Install on Ubuntu/Debian
   curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # Install on Windows
   # Download from https://nodejs.org/
   ```

3. **Ollama** (for local LLM support)


## 🚀 Environment Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/your-username/mcp-labs
cd mcp-labs
```

### Step 2: Set Up Python Environment

```bash
# Create a virtual environment
python3 -m venv py_env

# Activate the environment
source py_env/bin/activate  # On macOS/Linux
# OR
py_env\Scripts\activate     # On Windows

# Add to your shell profile for auto-activation (optional)
echo "source $(pwd)/py_env/bin/activate" >> ~/.bashrc  # Bash
echo "source $(pwd)/py_env/bin/activate" >> ~/.zshrc   # Zsh
```

### Step 3: Install Python Dependencies

```bash
# Ensure virtual environment is activated
source py_env/bin/activate

# Install all required packages
pip install --upgrade pip
pip install mcp mcp[cli] mcp[inspector] fastapi uvicorn pydantic fastmcp crewai langchain_ollama langgraph langchain_mcp_adapters python-jose

# Or install from requirements file
pip install -r requirements.txt
```

### Step 4: Install Node.js Dependencies

```bash
# Install MCP Inspector globally
npm install -g @modelcontextprotocol/inspector

# Verify installation
npx @modelcontextprotocol/inspector --version
```

### Step 5: Set Up Ollama

If you want to run local LLMs for testing:

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
ollama serve &

# Pull a model (this may take several minutes)
ollama pull llama3.2

# Verify installation
ollama list
```

## 🧪 Quick Test Setup

### Option 1: Automated Setup (Recommended)

Use the provided setup script:

```bash
# Make the script executable
chmod +x scripts/working_local_setup.sh

# Run the complete setup
./scripts/working_local_setup.sh
```

This will:
- Set up the Python virtual environment
- Install all dependencies
- Start a local MCP server
- Start the MCP Inspector
- Open your browser to the inspector interface

### Option 2: Manual Setup

1. **Start a Local MCP Server**:
   ```bash
   # Activate Python environment
   source py_env/bin/activate
   
   # Run a simple test server
   python3 simple_local_server.py
   ```

2. **Start MCP Inspector**:
   ```bash
   # In a new terminal
   export DANGEROUSLY_OMIT_AUTH=true
   npx @modelcontextprotocol/inspector
   ```

3. **Connect in Browser**:
   - Open http://localhost:6274
   - Enter Server URL: `http://localhost:8000/mcp`
   - Select Transport: `streamable-http`
   - Click Connect

## 🗂️ Project Structure

```
mcp-labs/
├── py_env/                 # Python virtual environment
├── lab2/                   # Lab 2 exercises
│   ├── mcp_server.py      # Basic MCP server
│   ├── mcp_travel_server.py # Travel helper server
│   └── mcp_client.py      # MCP client examples
├── lab3/                   # Lab 3 - Security
│   ├── secure_server.py   # JWT-protected server
│   └── auth_server.py     # Authentication server
├── lab4/                   # Lab 4 - Advanced topics
├── scripts/               # Utility scripts
│   ├── working_local_setup.sh    # Complete setup
│   ├── clear_chrome_cache.sh     # Browser cache clearing
│   └── setup.sh          # Environment setup
├── requirements.txt       # Python dependencies
└── LOCAL_SETUP.md        # This file
```

## 🔧 Development Workflows

### Running Individual Labs

```bash
# Activate environment
source py_env/bin/activate

# Run Lab 2 travel server
cd lab2
python3 mcp_travel_server.py

# Run Lab 3 secure server
cd lab3
python3 secure_server.py

# Run Lab 4 examples
cd lab4
python3 mcp_server.py
```

### Testing with MCP Inspector

1. **Start your MCP server** (any of the lab servers)
2. **Start MCP Inspector**:
   ```bash
   npx @modelcontextprotocol/inspector
   ```
3. **Connect in browser** at http://localhost:6274

### Common Development Tasks

- **Install new Python packages**: `pip install package-name`
- **Update dependencies**: `pip install --upgrade -r requirements.txt`
- **Clear browser cache**: `./scripts/clear_chrome_cache.sh`
- **Reset environment**: Delete `py_env/` and start over

## 🐛 Troubleshooting

### Python Issues

```bash
# If virtual environment activation fails
python3 -m venv --clear py_env
source py_env/bin/activate

# If pip install fails with permissions
pip install --user package-name

# If Python path issues
which python3
which pip3
```

### Node.js/NPX Issues

```bash
# If npx command not found
npm install -g npx

# If MCP Inspector fails to start
npm cache clean --force
npm install -g @modelcontextprotocol/inspector --force
```



### Port Conflicts

```bash
# Kill processes on MCP ports
kill -9 $(lsof -t -i:8000) 2>/dev/null || true
kill -9 $(lsof -t -i:6274) 2>/dev/null || true
kill -9 $(lsof -t -i:6277) 2>/dev/null || true
```

## 📚 Additional Resources

- **MCP Documentation**: https://docs.anthropic.com/claude/docs/mcp
- **FastMCP Documentation**: https://github.com/jlowin/fastmcp
- **MCP Inspector**: https://github.com/modelcontextprotocol/inspector
- **Python Virtual Environments**: https://docs.python.org/3/tutorial/venv.html

## 🆘 Getting Help

If you encounter issues:

1. **Check the troubleshooting section above**
2. **Verify all prerequisites are installed correctly**
3. **Try the automated setup script**: `./scripts/working_local_setup.sh`
4. **Use incognito browser mode** to avoid cache issues
5. **Check that all required ports (8000, 6274, 6277) are available**

## 🎯 Quick Start Commands

```bash
# Complete setup in one command
git clone <repo-url> && cd mcp-labs && ./scripts/working_local_setup.sh

# Manual step-by-step
python3 -m venv py_env
source py_env/bin/activate
pip install -r requirements.txt
python3 simple_local_server.py &
npx @modelcontextprotocol/inspector
```

Now you should have a fully functional local MCP development environment equivalent to the GitHub Codespace setup!
