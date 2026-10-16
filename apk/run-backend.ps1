# Listen on every interface so a phone on the same Wi-Fi can reach this PC.
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$backend = Join-Path $root "backend"
$python = Join-Path $backend "venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
  throw "Backend venv not found at $python"
}

$conns = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conns) {
  $conns.OwningProcess | Sort-Object -Unique | ForEach-Object {
    Stop-Process -Id $_ -Force -ErrorAction SilentlyContinue
  }
  Start-Sleep -Seconds 1
}

Write-Host "PhishEye API on http://0.0.0.0:8000 (reachable from your phone on this Wi-Fi)"
Set-Location $backend
& $python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
