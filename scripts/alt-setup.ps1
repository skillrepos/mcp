# setup.ps1 - PowerShell setup for mcp (Python, NumPy<2, torch)

Write-Host "🛠️  Setting up environment for mcp..."

# 1. Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Error "Python 3 not found. Please install Python and try again."
    exit 1
}

# 2. Create virtual environment
Write-Host "`n[1/6] Creating virtual environment..."
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Error "Virtual environment creation failed."
    exit $LASTEXITCODE
}

# 3. Activate virtual environment
Write-Host "`n[2/6] Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# 4. Upgrade pip
Write-Host "`n[3/6] Upgrading pip..."
pip install --upgrade pip

# 5. Install dependencies (excluding torch)
Write-Host "`n[4/6] Installing requirements (excluding torch)..."
Get-Content requirements.txt | Where-Object { $_ -notmatch "^torch" } | Set-Content tmp_requirements.txt
pip install -r tmp_requirements.txt

# 6. Pin NumPy and install torch
Write-Host "`n[5/6] Installing numpy<2 and torch..."
pip install "numpy<2"
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

# 7. Done
Write-Host "`n✅ Setup complete. To activate the environment:"
Write-Host "   .\.venv\Scripts\Activate.ps1"

