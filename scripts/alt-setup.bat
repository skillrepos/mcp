@echo off
REM setup.bat - Windows CMD setup for mcp (Python, NumPy<2, torch)

echo [1/6] Checking for Python...
where python >nul 2>nul
if errorlevel 1 (
    echo Error: Python not found. Please install Python 3.
    exit /b 1
)

echo [2/6] Creating virtual environment...
python -m venv .venv
if errorlevel 1 (
    echo Failed to create virtual environment.
    exit /b 1
)

echo [3/6] Activating virtual environment...
call .venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    exit /b 1
)

echo [4/6] Upgrading pip...
pip install --upgrade pip

echo [5/6] Installing dependencies (excluding torch)...
powershell -Command "Get-Content requirements.txt | Where-Object {$_ -notmatch '^torch'} | Set-Content tmp_requirements.txt"
pip install -r tmp_requirements.txt

echo [6/6] Pinning numpy and installing torch...
pip install "numpy<2"
pip install torch==2.2.2 --index-url https://download.pytorch.org/whl/cpu

echo.
echo ✅ Setup complete. Activate your environment with:
echo    call .venv\Scripts\activate.bat

