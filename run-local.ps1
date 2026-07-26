$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDirectory = Join-Path $projectRoot "backend"
$frontendDirectory = Join-Path $projectRoot "frontend"
$backendPython = Join-Path $backendDirectory ".venv\Scripts\python.exe"
$backendEnv = Join-Path $backendDirectory ".env"

if (-not (Test-Path -LiteralPath $backendPython)) {
    throw "Backend environment missing. Create backend\.venv and install backend\requirements.txt first."
}

if (-not (Test-Path -LiteralPath $backendEnv)) {
    throw "backend\.env is missing. Copy backend\.env.example to backend\.env and configure it first."
}

$npmCommand = Get-Command npm.cmd -ErrorAction SilentlyContinue
$npmPath = if ($npmCommand) {
    $npmCommand.Source
} else {
    "C:\Program Files\nodejs\npm.cmd"
}

if (-not (Test-Path -LiteralPath $npmPath)) {
    throw "npm was not found. Install Node.js 22.13 or newer and restart PowerShell."
}

if (-not (Test-Path -LiteralPath (Join-Path $frontendDirectory "node_modules"))) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $frontendDirectory
    try {
        & $npmPath install
        if ($LASTEXITCODE -ne 0) {
            throw "Frontend dependency installation failed."
        }
    } finally {
        Pop-Location
    }
}

$backendCommand = @"
Set-Location -LiteralPath '$backendDirectory'
& '$backendPython' -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
"@

$frontendCommand = @"
Set-Location -LiteralPath '$frontendDirectory'
& '$npmPath' run dev
"@

$backendProcess = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList "-NoExit", "-Command", $backendCommand `
    -WorkingDirectory $backendDirectory `
    -PassThru

$frontendProcess = Start-Process `
    -FilePath "powershell.exe" `
    -ArgumentList "-NoExit", "-Command", $frontendCommand `
    -WorkingDirectory $frontendDirectory `
    -PassThru

Write-Host ""
Write-Host "Model Meter is starting locally." -ForegroundColor Green
Write-Host "Frontend: http://localhost:3000"
Write-Host "API docs: http://127.0.0.1:8000/docs"
Write-Host ""
Write-Host "Close the two server windows to stop the application."
Write-Host "Backend PID: $($backendProcess.Id) | Frontend PID: $($frontendProcess.Id)"
