# Check .env for weekly job (does not print secrets). See scripts/check_weekly_env.py
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$py = Join-Path $root "scripts\check_weekly_env.py"
if (-not (Test-Path $py)) {
    Write-Error "Missing $py"
}
python $py
exit $LASTEXITCODE
