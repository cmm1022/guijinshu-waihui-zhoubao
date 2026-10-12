#!/usr/bin/env bash
# Cloud Automation / cron 入口：兼容仅有 python3、~/.local/bin 未进 PATH 的 Linux 环境。
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

export PATH="${HOME}/.local/bin:${PATH}"

if command -v python >/dev/null 2>&1; then
  PYTHON=python
elif command -v python3 >/dev/null 2>&1; then
  PYTHON=python3
else
  echo "错误: 未找到 python 或 python3" >&2
  exit 127
fi

"$PYTHON" -m pip install -r requirements.txt

CHANNEL="${CMS_BROWSER_CHANNEL:?缺少 CMS_BROWSER_CHANNEL（与 Playwright 安装通道一致）}"
"$PYTHON" -m playwright install "$CHANNEL"

export CMS_HEADLESS="${CMS_HEADLESS:-1}"

exec "$PYTHON" -m src.run_weekly
