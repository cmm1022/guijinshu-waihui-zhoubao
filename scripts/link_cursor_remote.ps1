# 关联 Cursor Origin 远程并 push（需先在浏览器创建仓库并复制 HTTPS 地址）
param(
    [Parameter(Mandatory = $true)]
    [string]$RemoteUrl
)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
if (git remote get-url origin 2>$null) {
    Write-Host "已存在 origin: $(git remote get-url origin)"
    $ans = Read-Host "是否改为新地址? (y/N)"
    if ($ans -ne "y") { exit 0 }
    git remote remove origin
}
git remote add origin $RemoteUrl
git push -u origin master
Write-Host "已 push 到 origin/master。"
