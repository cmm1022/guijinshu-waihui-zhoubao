# Check .env has required Automation variable names (does not print secrets)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$envFile = Join-Path $root ".env"
$required = @(
    "EMAIL_USER", "EMAIL_PASSWORD", "IMAP_HOST", "IMAP_PORT",
    "CMS_BASE_URL", "CMS_EMAIL", "CMS_PASSWORD",
    "CMS_EDITOR_URL", "CMS_BROWSER_CHANNEL", "CMS_HEADLESS"
)
if (-not (Test-Path $envFile)) {
    Write-Error ".env not found. Copy from .env.example and fill in values."
}
$lines = Get-Content $envFile -Encoding UTF8
$keys = @{}
foreach ($line in $lines) {
    if ($line -match '^\s*#' -or $line -match '^\s*$') { continue }
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=') {
        $keys[$Matches[1]] = $true
    }
}
$missing = @($required | Where-Object { -not $keys.ContainsKey($_) })
if ($missing.Count -gt 0) {
    Write-Host "Missing keys: $($missing -join ', ')"
    exit 1
}
Write-Host "OK: .env contains all $($required.Count) required keys."
Write-Host "Add the same names in Cursor Automations -> Secrets (values from .env)."
