FROM mcr.microsoft.com/devcontainers/base:bookworm

# Install prerequisites
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        zstd curl ca-certificates python3 python3-venv python3-pip && \
    rm -rf /var/lib/apt/lists/*

# Pre-build the Python virtual environment
# Install CPU-only PyTorch FIRST to avoid pulling in GPU/triton packages
COPY requirements.txt /tmp/requirements.txt
RUN python3 -m venv /opt/py_env && \
    /opt/py_env/bin/pip install --no-cache-dir \
        torch torchvision torchaudio \
        --index-url https://download.pytorch.org/whl/cpu && \
    /opt/py_env/bin/pip install --no-cache-dir -r /tmp/requirements.txt && \
    /opt/py_env/bin/pip uninstall -y \
        triton nvidia-cublas-cu12 nvidia-cuda-cupti-cu12 \
        nvidia-cuda-nvrtc-cu12 nvidia-cuda-runtime-cu12 \
        nvidia-cufft-cu12 nvidia-cufile-cu12 \
        nvidia-curand-cu12 nvidia-cusparse-cu12 \
        nvidia-cusparselt-cu12 nvidia-nccl-cu12 \
        nvidia-nvjitlink-cu12 nvidia-nvshmem-cu12 \
        nvidia-nvtx-cu12 2>/dev/null || true && \
    find /opt/py_env -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true && \
    find /opt/py_env -name "*.pyc" -delete 2>/dev/null || true

# Pre-download the sentence-transformers embedding model
RUN /opt/py_env/bin/python -c \
    "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Install Node.js LTS
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Pre-install Ollama (binary only — no model pull)
RUN curl -fsSL https://ollama.com/install.sh | sh

