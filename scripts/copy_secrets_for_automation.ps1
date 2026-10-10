# Copy each Automation secret from .env to clipboard (one key per Enter)
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$envFile = Join-Path $root ".env"
$order = @(
    "EMAIL_USER", "EMAIL_PASSWORD", "IMAP_HOST", "IMAP_PORT", "MAIL_SENDER",
    "CMS_BASE_URL", "CMS_EMAIL", "CMS_PASSWORD",
    "CMS_EDITOR_URL", "CMS_BROWSER_CHANNEL", "CMS_HEADLESS"
)
if (-not (Test-Path $envFile)) { Write-Error ".env not found" }
$vals = @{}
Get-Content $envFile -Encoding UTF8 | ForEach-Object {
    $line = $_.Trim()
    if ($line -match '^\s*#' -or $line -eq "") { return }
    if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
        $k = $Matches[1]
        $v = $Matches[2].Trim()
        if ($v.StartsWith('"') -and $v.EndsWith('"')) { $v = $v.Substring(1, $v.Length - 2) }
        $vals[$k] = $v
    }
}
Write-Host "Automations -> Secrets: create each name, paste from clipboard, Save."
Write-Host "Press Enter to start (Ctrl+C to abort)."
[void][Console]::ReadLine()
foreach ($key in $order) {
    if (-not $vals.ContainsKey($key)) {
        Write-Host "Skip $key (not in .env)"
        continue
    }
    Set-Clipboard -Value $vals[$key]
    Write-Host ">>> Clipboard: $key  (paste in Secrets, then Enter for next)"
    [void][Console]::ReadLine()
}
Write-Host "Done."
