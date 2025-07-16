<#
    local_mcpi.ps1 - Launches the MCP Inspector for a given GitHub Codespace

    USAGE:
      Open PowerShell and run:
          .\local_mcpi.ps1 <your-codespace-name>

    EXAMPLE:
          .\local_mcpi.ps1 bug-free-pancake-p7575jwp9p3975g

    REQUIREMENTS:
      • PowerShell 5+ (Windows 10/11)
      • Node.js and npm installed (https://nodejs.org)
      • Port 6277 must be available (used by Inspector UI)

    TIPS:
      If you get execution policy errors, run:
          Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$CodespaceName
)

Write-Host "🛠️  Starting MCP Inspector for codespace: $CodespaceName"

# 1. Kill processes on ports 6274 and 6277
$portsToKill = @(6274, 6277)
foreach ($port in $portsToKill) {
    $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    foreach ($conn in $connections) {
        try {
            $pid = $conn.OwningProcess
            if ($pid) {
                Stop-Process -Id $pid -Force -ErrorAction Stop
                Write-Host "✅ Killed process $pid on port $port"
            }
        } catch {
            Write-Warning "⚠️  Failed to stop process on port $port: $_"
        }
    }
}

# 2. Check for npm
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "`n❌ npm not found. Please install Node.js from https://nodejs.org before continuing." -ForegroundColor Red
    exit 1
}
Write-Host "✅ npm is installed."

# 3. Check for npx
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "🔧 Installing npx..."
    npm install -g npx
} else {
    Write-Host "✅ npx is available."
}

# 4. Build MCP Inspector target URL
$McpUrl = "https://${CodespaceName}-8000.app.github.dev/mcp/"
Write-Host "`n🚀 Launching MCP Inspector for: $McpUrl"

# Start inspector in new PowerShell window
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx @modelcontextprotocol/inspector --url `"$McpUrl`" --protocol streaming-http"

# 5. Open browser to Inspector UI
$InspectorUrl = "http://localhost:6277"
Write-Host "`n🌐 Opening browser to Inspector at: $InspectorUrl"
Start-Process $InspectorUrl
