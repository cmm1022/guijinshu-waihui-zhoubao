# One-shot: API Key -> sync Cloud Secrets -> open Automations (ASCII only for encoding)
$ErrorActionPreference = "Stop"
$root = "D:\cursor项目\贵金属外汇周报"
Set-Location $root

Write-Host ""
Write-Host "=== Weekly report: Cloud Secrets setup ===" -ForegroundColor Cyan
Write-Host ""
Write-Host "Step 1: Browser opens Cursor Settings -> API Keys -> Create -> copy key"
Start-Process "https://cursor.com/dashboard?tab=settings"
Start-Sleep -Seconds 2

$key = Read-Host "Step 2: Paste API Key here and press Enter"
$key = $key.Trim()
if ($key.Length -lt 10) { throw "API Key too short" }

$env:CURSOR_API_KEY = $key
Write-Host "Step 3: Syncing secrets from .env to Cloud environment ..." -ForegroundColor Yellow
python "$root\scripts\sync_cursor_cloud_secrets.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Step 4: Opening Automations. Pick environment guijinshu-waihui-zhoubao, repo main, Save." -ForegroundColor Green
Start-Process "https://cursor.com/automations"
Write-Host "Done." -ForegroundColor Green
Read-Host "Press Enter to close"
