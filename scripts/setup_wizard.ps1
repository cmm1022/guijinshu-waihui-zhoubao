# One-window setup: create Cursor repo (browser) -> paste clone URL -> push -> copy secrets
$ErrorActionPreference = "Stop"
$root = "D:\cursor项目\贵金属外汇周报"
Set-Location $root

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Weekly report CMS - setup wizard" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Opening Cursor Codebase in browser..." -ForegroundColor Yellow
Start-Process "https://cursor.com/codebase/get-started"
Write-Host "      -> Log in, create repo name: guijinshu-waihui-zhoubao"
Write-Host "      -> Copy HTTPS clone URL (https://origin.cursor.com/...)"
Write-Host ""

$defaultUrl = "https://origin.cursor.com/guijinshu-waihui-zhoubao/guijinshu-waihui-zhoubao.git"
Write-Host "Default: $defaultUrl"
$url = Read-Host "[2/4] Paste clone URL (Enter = use default)"
$url = ($url.Trim().Trim('"'))
if ($url -eq "") { $url = $defaultUrl }
if ($url -notmatch '^https?://') {
    Write-Error "Invalid URL. Paste the full HTTPS clone link."
}

if (git remote get-url origin 2>$null) {
    git remote remove origin
}
git remote add origin $url
Write-Host "[3/4] Pushing to origin (browser login may appear)..." -ForegroundColor Yellow
git push -u origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host "Push failed. Complete Cursor login in browser, then run:" -ForegroundColor Red
    Write-Host "  cd `"$root`"; git push -u origin master"
    Read-Host "Press Enter after push succeeds to continue secrets"
}

Write-Host "[4/4] Opening Automations and secret copy helper..." -ForegroundColor Yellow
Start-Process "https://cursor.com/automations"
Start-Sleep -Seconds 2
& "$root\scripts\copy_secrets_for_automation.ps1"

Write-Host ""
Write-Host "Last step in Automations UI:" -ForegroundColor Green
Write-Host "  - Pick repo guijinshu-waihui-zhoubao"
Write-Host "  - Schedule: Monday 09:00 Asia/Shanghai"
Write-Host "  - Save automation"
Read-Host "Press Enter to close this window"
