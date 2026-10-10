# 尽量一键：创建 API Key -> 同步 Secrets -> 打开 Automations
$ErrorActionPreference = "Stop"
$root = "D:\cursor项目\贵金属外汇周报"
Set-Location $root

Write-Host "Step 1: 浏览器打开 Cursor API Keys（登录后 Create key，复制密钥）" -ForegroundColor Cyan
Start-Process "https://cursor.com/dashboard?tab=settings"
Start-Sleep -Seconds 2

$key = Read-Host "Step 2: 将 API Key 粘贴到此处（仅本机使用，不会显示在聊天里）"
$key = $key.Trim()
if ($key.Length -lt 10) { throw "API Key 过短，请重试" }

$env:CURSOR_API_KEY = $key
Write-Host "Step 3: 同步 .env 中的邮件/CMS 密钥到 Cloud Agents 环境 …" -ForegroundColor Cyan
python "$root\scripts\sync_cursor_cloud_secrets.py"
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

Write-Host "Step 4: 打开 Automations（请选择环境 guijinshu-waihui-zhoubao 并 Save）" -ForegroundColor Cyan
Start-Process "https://cursor.com/automations"
Write-Host "完成。" -ForegroundColor Green
