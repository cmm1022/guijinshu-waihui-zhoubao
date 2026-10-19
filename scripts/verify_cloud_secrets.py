"""检查 Cursor Cloud 环境是否已配置周报所需 Secrets（不打印密钥值）。"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ".env"
REPO_SLUG = "github.com/cmm1022/guijinshu-waihui-zhoubao"
ENV_NAME = "guijinshu-waihui-zhoubao"
API_BASE = "https://api.cursor.com/v1"

REQUIRED = [
    "EMAIL_USER",
    "EMAIL_PASSWORD",
    "IMAP_HOST",
    "IMAP_PORT",
    "CMS_BASE_URL",
    "CMS_EDITOR_URL",
    "CMS_BROWSER_CHANNEL",
    "CMS_HEADLESS",
    "CMS_PUBLISH_MODE",
    "CMS_TENANT_PUBLISHERS",
    "CMS_TENANT_ZRCUB_PASSWORD",
    "CMS_TENANT_PSBC_PASSWORD",
    "CMS_TENANT_HZBANK_PASSWORD",
    "CMS_TENANT_BCM_PASSWORD",
    "REPORT_TZ",
]
OPTIONAL = ["MAIL_SENDER", "CMS_EMAIL", "CMS_PASSWORD"]


def _load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def _request(method: str, path: str, api_key: str) -> dict:
    import base64

    req = urllib.request.Request(
        f"{API_BASE}{path}",
        method=method,
        headers={"Content-Type": "application/json"},
    )
    token = base64.b64encode(f"{api_key}:".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    with urllib.request.urlopen(req, timeout=60) as resp:
        raw = resp.read().decode("utf-8")
        return json.loads(raw) if raw else {}


def _find_environment_id(api_key: str) -> str | None:
    data = _request("GET", "/environments?limit=100", api_key)
    for item in data.get("items", []):
        repos = item.get("repos") or []
        for r in repos:
            url = (r.get("url") or "").lower()
            if REPO_SLUG in url or "guijinshu-waihui-zhoubao" in url:
                return item["id"]
        if item.get("name") == ENV_NAME:
            return item["id"]
    return None


def _list_secret_names(api_key: str, env_id: str) -> set[str]:
    """尝试多种 API 形态，返回已配置的 secret 名称集合。"""
    names: set[str] = set()
    paths = (
        f"/environments/{env_id}/secrets",
        f"/environments/{env_id}?include=secrets",
    )
    for path in paths:
        try:
            data = _request("GET", path, api_key)
        except urllib.error.HTTPError:
            continue
        if isinstance(data.get("items"), list):
            for it in data["items"]:
                n = it.get("name") or it.get("key")
                if n:
                    names.add(str(n))
        if isinstance(data.get("secrets"), list):
            for it in data["secrets"]:
                n = it.get("name") or it.get("key")
                if n:
                    names.add(str(n))
        if isinstance(data, dict) and data.get("name"):
            pass
    return names


def main() -> int:
    dot = _load_dotenv(ENV_FILE)
    api_key = os.getenv("CURSOR_API_KEY", "").strip() or dot.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print("无法核对云端：缺少 CURSOR_API_KEY。", file=sys.stderr)
        print(
            "请任选其一后重跑本脚本：\n"
            "  1) .env 增加 CURSOR_API_KEY=… 再运行 python scripts/sync_cursor_cloud_secrets.py\n"
            "  2) powershell -ExecutionPolicy Bypass -File .\\scripts\\setup_cloud_complete.ps1",
            file=sys.stderr,
        )
        return 2

    env_id = _find_environment_id(api_key)
    if not env_id:
        print(f"未找到 Cloud 环境（仓库 {REPO_SLUG} / 名称 {ENV_NAME!r}）", file=sys.stderr)
        print("请先运行: python scripts/sync_cursor_cloud_secrets.py", file=sys.stderr)
        return 1

    print(f"Cloud 环境 ID: {env_id}")
    cloud_names = _list_secret_names(api_key, env_id)

    if not cloud_names:
        print(
            "警告: API 未返回 Secrets 列表（可能权限或接口变更）。"
            "将改为核对本地 .env 是否齐全，并建议执行 sync 脚本覆盖写入。"
        )
        local_missing = [n for n in REQUIRED if not dot.get(n)]
        if local_missing:
            print(f"本地 .env 缺少: {', '.join(local_missing)}")
            return 1
        print("本地 .env 已含全部必需项。请运行 sync 脚本写入 Cloud：")
        print("  python scripts/sync_cursor_cloud_secrets.py")
        return 3

    missing = [n for n in REQUIRED if n not in cloud_names]
    present_opt = [n for n in OPTIONAL if n in cloud_names]
    print(f"云端已配置 {len(cloud_names)} 个 Secret")
    if missing:
        print(f"云端缺少必需项 ({len(missing)}): {', '.join(missing)}")
        print("修复: python scripts/sync_cursor_cloud_secrets.py")
        return 1

    print("云端必需 Secrets: 全部齐全")
    if present_opt:
        print(f"可选已配置: {', '.join(present_opt)}")
    print("请在 Automation 中确认 Environment 绑定该 Cloud 环境并已 Save。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
