# Push to GitHub via local proxy (Clash etc. on 7890)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $root
$proxy = "http://127.0.0.1:7890"
$env:HTTP_PROXY = $proxy
$env:HTTPS_PROXY = $proxy
git -c http.proxy=$proxy -c https.proxy=$proxy push @args
