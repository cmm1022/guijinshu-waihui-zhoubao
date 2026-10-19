"""将本地 .env 中的周报密钥同步到 Cursor Cloud Agents 环境（需 CURSOR_API_KEY）。"""

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
REPO_URL = f"https://github.com/cmm1022/guijinshu-waihui-zhoubao"
ENV_NAME = "guijinshu-waihui-zhoubao"

SECRET_NAMES = [
    "EMAIL_USER",
    "EMAIL_PASSWORD",
    "IMAP_HOST",
    "IMAP_PORT",
    "MAIL_SENDER",
    "CMS_BASE_URL",
    "CMS_EMAIL",
    "CMS_PASSWORD",
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

API_BASE = "https://api.cursor.com/v1"


def _load_dotenv(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        v = v.strip().strip('"').strip("'")
        out[k] = v
    return out


def _request(method: str, path: str, api_key: str, body: dict | None = None) -> dict:
    url = f"{API_BASE}{path}"
    data = None
    headers = {"Content-Type": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    import base64

    token = base64.b64encode(f"{api_key}:".encode()).decode()
    req.add_header("Authorization", f"Basic {token}")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"HTTP {e.code} {path}: {err}") from e


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


def _create_environment(api_key: str) -> str:
    env_json = (ROOT / ".cursor" / "environment.json").read_text(encoding="utf-8")
    body = {
        "owner": "personal",
        "name": ENV_NAME,
        "repos": [{"url": REPO_URL}],
        "environmentJson": json.dumps(json.loads(env_json)),
    }
    try:
        data = _request("POST", "/environments", api_key, body)
        return data["id"]
    except RuntimeError as exc:
        if "environment_name_conflict" in str(exc) or "409" in str(exc):
            eid = _find_environment_id(api_key)
            if eid:
                return eid
        raise


def main() -> int:
    dot = _load_dotenv(ENV_FILE)
    api_key = os.getenv("CURSOR_API_KEY", "").strip() or dot.get("CURSOR_API_KEY", "").strip()
    if not api_key:
        print(
            "缺少 CURSOR_API_KEY。\n"
            "1. 打开 https://cursor.com/dashboard?tab=settings → API Keys 创建密钥\n"
            "2. 在 .env 增加一行 CURSOR_API_KEY=你的密钥\n"
            "3. 再运行: python scripts/sync_cursor_cloud_secrets.py",
            file=sys.stderr,
        )
        return 1

    env_id = _find_environment_id(api_key)
    if not env_id:
        print(f"未找到含 {REPO_URL} 的环境，正在创建 {ENV_NAME!r} …")
        env_id = _create_environment(api_key)
    print(f"环境 ID: {env_id}")

    missing = [n for n in SECRET_NAMES if not dot.get(n)]
    if missing:
        print(f"警告: .env 缺少 {', '.join(missing)}", file=sys.stderr)

    for name in SECRET_NAMES:
        value = dot.get(name)
        if not value:
            print(f"跳过 {name}（无值）")
            continue
        _request(
            "PUT",
            f"/environments/{env_id}/secrets/{name}",
            api_key,
            {"value": value, "type": "runtime_secret", "repos": [REPO_SLUG]},
        )
        print(f"已设置 {name}")

    print("完成。请在 Automation 里选择 Cloud 环境并 Save。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
