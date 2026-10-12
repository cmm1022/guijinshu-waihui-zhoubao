"""检查每周任务所需配置（不打印密码）。支持本地 .env 或 Cloud Secrets 环境变量。"""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

ENV_FILE = ROOT / ".env"


def _keys_from_dotenv_file() -> set[str]:
    keys: set[str] = set()
    if not ENV_FILE.is_file():
        return keys
    for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        keys.add(line.split("=", 1)[0].strip())
    return keys


def _configured_keys() -> set[str]:
    keys = _keys_from_dotenv_file()
    for name, value in os.environ.items():
        if value.strip():
            keys.add(name)
    return keys


def main() -> int:
    keys = _configured_keys()
    if not keys:
        print(
            "错误: 未找到 .env，且当前进程环境变量也为空。"
            "本地请从 .env.example 复制；云端请在 Cloud Agents → Secrets 配置。",
            file=sys.stderr,
        )
        return 1

    if not ENV_FILE.is_file():
        print("（无 .env 文件，仅根据已设置的环境变量检查）")
    email_keys = [
        "EMAIL_USER",
        "EMAIL_PASSWORD",
        "IMAP_HOST",
        "IMAP_PORT",
        "CMS_BASE_URL",
        "CMS_EDITOR_URL",
        "CMS_BROWSER_CHANNEL",
        "CMS_HEADLESS",
    ]
    missing_email = [k for k in email_keys if k not in keys]
    if missing_email:
        print(f"缺少收信/CMS 基础项: {', '.join(missing_email)}")
        return 1

    try:
        from config import load_settings

        settings = load_settings()
    except RuntimeError as exc:
        print(f"配置错误: {exc}")
        return 1

    print(f"发布模式: {settings.publish_mode}")
    if settings.publish_mode == "per_tenant":
        if not settings.tenant_publishers:
            print("错误: per_tenant 但未解析到 CMS_TENANT_PUBLISHERS")
            return 1
        op_on = __import__("os").getenv("CMS_OPERATOR_PUBLISH", "1").strip().lower() not in (
            "0",
            "false",
            "no",
        )
        if op_on:
            if not settings.cms_email or not settings.cms_password:
                print("缺少 CMS_EMAIL / CMS_PASSWORD（分租户模式下默认运营账号也会发布）")
                return 1
            print(f"运营账号: {settings.cms_email}（随后各租户再各发 1 篇）")
        print(f"租户数量: {len(settings.tenant_publishers)}")
        for t in settings.tenant_publishers:
            print(f"  - {t.name} ({t.email}) -> {', '.join(sorted(t.keywords))}")
        cloud_tenant = [
            "CMS_PUBLISH_MODE",
            "CMS_TENANT_PUBLISHERS",
            "CMS_TENANT_ZRCUB_PASSWORD",
            "CMS_TENANT_PSBC_PASSWORD",
            "CMS_TENANT_HZBANK_PASSWORD",
            "CMS_TENANT_BCM_PASSWORD",
        ]
        missing_cloud = [k for k in cloud_tenant if k not in keys]
        if missing_cloud:
            print(f"提示: Cloud 环境建议同步这些项: {', '.join(missing_cloud)}")
    else:
        if "CMS_EMAIL" not in keys or "CMS_PASSWORD" not in keys:
            print("缺少 CMS_EMAIL / CMS_PASSWORD（运营账号模式需要）")
            return 1
        print("运营账号模式: 需 CMS_EMAIL + 内容同步")

    print("OK: 配置检查通过。")
    print(
        "云端: 请在 Cloud Agents 环境 Secrets 中配置与 .env 同名的变量；"
        "或运行 setup_cloud_complete.ps1 / sync_cursor_cloud_secrets.py（需 CURSOR_API_KEY）。"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
