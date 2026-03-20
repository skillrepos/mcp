#!/usr/bin/env bash

PYTHON_ENV=$1
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -d "/opt/py_env" ]; then
    # Copy pre-built venv from Docker image and fix paths
    cp -a /opt/py_env ./$PYTHON_ENV
    # Update venv paths to point to the workspace location
    sed -i "s|/opt/py_env|$(pwd)/$PYTHON_ENV|g" ./$PYTHON_ENV/bin/activate
    sed -i "s|/opt/py_env|$(pwd)/$PYTHON_ENV|g" ./$PYTHON_ENV/bin/pip*
    sed -i "s|/opt/py_env|$(pwd)/$PYTHON_ENV|g" ./$PYTHON_ENV/pyvenv.cfg 2>/dev/null || true
else
    # Fallback: create venv and install from scratch
    python3 -m venv ./$PYTHON_ENV
    source ./$PYTHON_ENV/bin/activate
    if [ -f "./requirements.txt" ]; then
        pip3 install -r "./requirements.txt"
    else
        pip3 install -r "$WORKSPACE_DIR/requirements/requirements.txt"
    fi
fi

# Ensure CPU-only PyTorch (no CUDA/GPU in Codespace)
./$PYTHON_ENV/bin/pip uninstall -y nvidia-cublas-cu12 nvidia-cuda-cupti-cu12 nvidia-cuda-nvrtc-cu12 nvidia-cuda-runtime-cu12 nvidia-cufft-cu12 nvidia-cufile-cu12 nvidia-curand-cu12 nvidia-cusparse-cu12 nvidia-cusparselt-cu12 nvidia-nccl-cu12 nvidia-nvjitlink-cu12 nvidia-nvshmem-cu12 nvidia-nvtx-cu12 2>/dev/null || true
./$PYTHON_ENV/bin/pip install --upgrade torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu 2>/dev/null || true

export PATH=./$PYTHON_ENV/bin:$PATH
grep -qxF "source $(pwd)/$PYTHON_ENV/bin/activate" ~/.bashrc || echo "source $(pwd)/$PYTHON_ENV/bin/activate" >> ~/.bashrc
