<#
    local_mcpi.ps1 <full-mcp-server-url>

    Example:
        .\local_mcpi.ps1 https://bug-free-pancake-p7575jwp9p3975g-8000.app.github.dev/mcp/

    Requirements:
        - Node.js + npm installed
        - Port 6277 available
        - Run PowerShell as administrator if needed

    If blocked by policy:
        Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
#>

param (
    [Parameter(Mandatory = $true)]
    [string]$McpUrl
)

Write-Host "🛠️  Starting MCP Inspector for URL: $McpUrl"

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

# 2. Ensure npm is available
if (-not (Get-Command npm -ErrorAction SilentlyContinue)) {
    Write-Host "`n❌ npm not found. Please install Node.js from https://nodejs.org" -ForegroundColor Red
    exit 1
}
Write-Host "✅ npm is installed."

# 3. Ensure npx is available
if (-not (Get-Command npx -ErrorAction SilentlyContinue)) {
    Write-Host "🔧 Installing npx..."
    npm install -g npx
} else {
    Write-Host "✅ npx is available."
}

# 4. Launch MCP Inspector in separate terminal
Write-Host "`n🚀 Launching MCP Inspector for: $McpUrl"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "npx @modelcontextprotocol/inspector --url `"$McpUrl`" --protocol streaming-http"

# 5. Open Inspector UI in browser
$InspectorUrl = "http://localhost:6277"
Write-Host "`n🌐 Opening MCP Inspector UI at $InspectorUrl"
Start-Process $InspectorUrl

