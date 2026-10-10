# GitHub setup: open new repo page -> push -> copy secrets
$ErrorActionPreference = "Stop"
$root = "D:\cursor项目\贵金属外汇周报"
$remote = "https://github.com/cmm1022/guijinshu-waihui-zhoubao.git"
Set-Location $root

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Weekly CMS - GitHub setup wizard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/3] Opening GitHub new repo page..." -ForegroundColor Yellow
Start-Process "https://github.com/new?name=guijinshu-waihui-zhoubao"
Write-Host "      Create PRIVATE repo guijinshu-waihui-zhoubao (no README), then return here."
Read-Host "Press Enter when repo is created"

git remote set-url origin $remote
if ($LASTEXITCODE -ne 0) { git remote add origin $remote }
git branch -M main
Write-Host "[2/3] git push -u origin main (GitHub login may appear)..." -ForegroundColor Yellow
git push -u origin main
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed. Fix auth and run: git push -u origin main" -ForegroundColor Red
    Read-Host "Press Enter after push succeeds"
}

Write-Host "[3/3] Automations + secrets helper..." -ForegroundColor Yellow
Start-Process "https://cursor.com/automations"
& "$root\scripts\copy_secrets_for_automation.ps1"

Write-Host "In Automations: repo cmm1022/guijinshu-waihui-zhoubao, branch main, Mon 09:00, Save."
Read-Host "Press Enter to close"
