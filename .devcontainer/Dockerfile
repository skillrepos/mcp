FROM mcr.microsoft.com/devcontainers/base:bookworm

# Install prerequisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        zstd curl ca-certificates python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Pre-build the Python virtual environment
# Install CPU-only PyTorch FIRST to avoid pulling in GPU/triton packages
COPY requirements.txt /tmp/requirements.txt
# `set -eux` + `;` separators, NOT an `&&` chain. The old form ended in
# `|| true`, and because shell `&&`/`||` are left-associative with equal
# precedence, a failure in venv or either pip short-circuited to that `|| true`
# and the layer exited 0 -- leaving an EMPTY /opt/py_env and pushing the error
# downstream to whatever imported from it first. The `|| true` below now sits
# only on the optional cleanup commands, where it belongs.
# UPGRADING pip FIRST IS LOAD-BEARING - do not drop that line.
# Bookworm's ensurepip seeds a venv with pip 23.0.1, which compares PEP 658
# sidecar metadata names RAW:
#     if metadata_dist.raw_name != req.req.name: raise MetadataInconsistent(...)
# typing_extensions 4.16.0 declares `Name: typing_extensions` (underscore) while
# pip asks for `typing-extensions` (dash), so the wheel is DISCARDED. pip then
# falls back to the sdist, whose build needs flit_core - not present on the
# PyTorch index, which `--index-url` makes the ONLY index in scope - and the
# install dies with "No matching distribution found for flit_core".
# pip >= 24.1 canonicalizes both names first and the failure vanishes.
# This broke with no change to this repo, when typing_extensions shipped a
# release using the underscore form.
#
# NOTE: keep comments OUT of the RUN body below. Docker's handling of comment
# lines inside a line continuation is subtle, and a `#` that survives the join
# comments out the remainder of the shell command - silently skipping installs.
RUN set -eux; \
    python3 -m venv /opt/py_env; \
    /opt/py_env/bin/pip install --no-cache-dir --upgrade pip setuptools wheel; \
    /opt/py_env/bin/pip --version; \
    /opt/py_env/bin/pip install --no-cache-dir \
        torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cpu; \
    /opt/py_env/bin/pip install --no-cache-dir -r /tmp/requirements.txt; \
    /opt/py_env/bin/python -c "import torch, fastmcp, sentence_transformers; \
        print('venv OK - torch', torch.__version__, '| fastmcp', fastmcp.__version__)"; \
    /opt/py_env/bin/pip uninstall -y \
        triton nvidia-cublas-cu12 nvidia-cuda-cupti-cu12 \
        nvidia-cuda-nvrtc-cu12 nvidia-cuda-runtime-cu12 \
        nvidia-cufft-cu12 nvidia-cufile-cu12 \
        nvidia-curand-cu12 nvidia-cusparse-cu12 \
        nvidia-cusparselt-cu12 nvidia-nccl-cu12 \
        nvidia-nvjitlink-cu12 nvidia-nvshmem-cu12 \
        nvidia-nvtx-cu12 2>/dev/null || true; \
    find /opt/py_env -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true; \
    find /opt/py_env -name "*.pyc" -delete 2>/dev/null || true

# Pre-download the sentence-transformers embedding model
RUN /opt/py_env/bin/python -c \
    "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Install Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Pre-warm the npx cache for the calculator-mcp training fork used in labs.
# Without this, the first `npx -y github:skillrepos/calculator-mcp` in a fresh
# codespace clones the repo, installs dev deps, and runs unbuild (~30-90s).
# Runs as the `vscode` user so the cache lands in /home/vscode/.npm/_npx where
# the Codespace session will hit it. `--help` forces the install+build path
# but exits before starting a server.
#
# NON-FATAL ON PURPOSE, and this is NOT the same mistake as the old `|| true`
# on the pip layer. That one masked failures in the commands that WERE the
# point of the layer. This command is a pure optimisation: if it fails the
# image is still completely correct, students just pay the npx cost once.
#
# But it must never fail SILENTLY - the measured "Lab 1 step 5 = 2s" depends on
# this cache being warm. Output is no longer sent to /dev/null (which hid the
# real error and left only npm's notices), and either outcome prints an
# unmistakable marker. GREP THE BUILD LOG FOR "npx cache pre-warm" AFTER EVERY
# REBUILD.
RUN set -eux; \
    if su vscode -c "npx -y github:skillrepos/calculator-mcp --help"; then \
        echo "npx cache pre-warm: OK"; \
    else \
        echo "npx cache pre-warm: FAILED - image is still usable, but Lab 1 step 5 will take 30-90s instead of ~2s"; \
    fi

# Pre-install Ollama (binary only — no model pull)
RUN curl -fsSL https://ollama.com/install.sh | sh

