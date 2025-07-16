#!/usr/bin/env bash
# setup.sh - env setup for mcp with PyTorch and NumPy pinning

set -e
echo "🛠️  Setting up environment for mcp..."

# 1. Check for Python 3
if ! command -v python3 &>/dev/null; then
  echo "Error: python3 is required." >&2
  exit 1
fi

# 2. Create and activate Python virtual environment
python3 -m venv .venv
echo "✅ Created virtual environment .venv/"
# shellcheck disable=SC1091
source .venv/bin/activate
echo "✅ Activated virtual environment."

# 3. Upgrade pip
pip install --upgrade pip

# 4. Install requirements (excluding torch)
grep -v '^torch' requirements.txt > /tmp/req_no_torch.txt
pip install -r /tmp/req_no_torch.txt

# 5. Pin NumPy to <2
pip install "numpy<2"

# 6. Architecture-aware PyTorch install
ARCH=$(uname -m)
echo "Detected architecture: $ARCH"

if [[ "$ARCH" == "arm64" && "$OSTYPE" == "darwin"* ]]; then
  echo "Installing Apple Silicon-compatible PyTorch..."
else
  echo "Installing standard CPU PyTorch..."
fi

# ✅ Correct version string
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# 7. Done
echo -e "\n✅ Setup complete. To activate your environment:"
echo "   source .venv/bin/activate"

