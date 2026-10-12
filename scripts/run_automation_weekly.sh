#!/usr/bin/env bash
# Cursor Automation / Cloud Agent 每周入口（Linux 仅有 python3，勿依赖 python 命令）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

export CMS_HEADLESS="${CMS_HEADLESS:-1}"

if ! command -v python3 >/dev/null 2>&1; then
  echo "错误: 未找到 python3" >&2
  exit 127
fi

python3 -m pip install -r requirements.txt
python3 -m playwright install
exec python3 -m src.run_weekly
