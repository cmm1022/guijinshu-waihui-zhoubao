"""从环境变量加载配置（本地 .env 或 Cursor Automation 密钥）。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT / ".env")


def _require(name: str) -> str:
    val = os.getenv(name, "").strip()
    if not val:
        raise RuntimeError(f"缺少环境变量: {name}")
    return val


@dataclass(frozen=True)
class Settings:
    email_user: str
    email_password: str
    imap_host: str
    imap_port: int
    mail_sender: str
    cms_base_url: str
    cms_email: str
    cms_password: str
    cms_dry_run: bool


def load_settings(*, require_cms: bool = True) -> Settings:
    email_user = _require("EMAIL_USER")
    email_password = _require("EMAIL_PASSWORD")
    imap_host = os.getenv("IMAP_HOST", "mail.myhexin.com").strip()
    imap_port = int(os.getenv("IMAP_PORT", "993"))
    mail_sender = os.getenv("MAIL_SENDER", "webdetect@myhexin.com").strip().lower()
    cms_base_url = os.getenv("CMS_BASE_URL", "https://prenewcms.wewecall.com:5443").rstrip("/")

    cms_dry_run = os.getenv("CMS_DRY_RUN", "").strip() in ("1", "true", "yes")
    if require_cms and not cms_dry_run:
        cms_email = _require("CMS_EMAIL")
        cms_password = _require("CMS_PASSWORD")
    else:
        cms_email = os.getenv("CMS_EMAIL", "").strip()
        cms_password = os.getenv("CMS_PASSWORD", "").strip()

    return Settings(
        email_user=email_user,
        email_password=email_password,
        imap_host=imap_host,
        imap_port=imap_port,
        mail_sender=mail_sender,
        cms_base_url=cms_base_url,
        cms_email=cms_email,
        cms_password=cms_password,
        cms_dry_run=cms_dry_run,
    )
