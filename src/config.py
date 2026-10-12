"""从环境变量加载配置（本地 .env 或 Cursor Automation 密钥）。"""

from __future__ import annotations

import json
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
class TenantPublisher:
    """各租户 CMS 账号：在该租户下直接发文（不依赖「内容同步」）。"""

    name: str
    keywords: frozenset[str]
    email: str
    password: str


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
    publish_mode: str  # operator_sync | per_tenant
    tenant_publishers: tuple[TenantPublisher, ...]


def _parse_tenant_publishers() -> tuple[TenantPublisher, ...]:
    raw = os.getenv("CMS_TENANT_PUBLISHERS", "").strip()
    if not raw:
        return ()
    try:
        items = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError("CMS_TENANT_PUBLISHERS 不是合法 JSON") from exc
    if not isinstance(items, list):
        raise RuntimeError("CMS_TENANT_PUBLISHERS 应为 JSON 数组")
    out: list[TenantPublisher] = []
    for i, it in enumerate(items):
        if not isinstance(it, dict):
            raise RuntimeError(f"CMS_TENANT_PUBLISHERS[{i}] 应为对象")
        name = str(it.get("name") or f"tenant_{i}").strip()
        kws = it.get("keywords") or []
        if isinstance(kws, str):
            kws = [kws]
        keywords = frozenset(str(k).strip() for k in kws if str(k).strip())
        if not keywords:
            raise RuntimeError(f"CMS_TENANT_PUBLISHERS[{i}] 缺少 keywords")
        email = str(it.get("email") or "").strip()
        if not email:
            raise RuntimeError(f"CMS_TENANT_PUBLISHERS[{i}] 缺少 email")
        password = str(it.get("password") or "").strip()
        pw_env = str(it.get("password_env") or "").strip()
        if not password and pw_env:
            password = os.getenv(pw_env, "").strip()
            if not password:
                raise RuntimeError(f"缺少租户密码环境变量: {pw_env}（{name}）")
        if not password:
            raise RuntimeError(
                f"CMS_TENANT_PUBLISHERS[{i}] 需 password 或 password_env（{name}）"
            )
        out.append(
            TenantPublisher(
                name=name, keywords=keywords, email=email, password=password
            )
        )
    return tuple(out)


def resolve_publish_mode(tenant_publishers: tuple[TenantPublisher, ...]) -> str:
    mode = os.getenv("CMS_PUBLISH_MODE", "").strip().lower()
    if mode in ("per_tenant", "tenant", "multi", "tenants"):
        return "per_tenant"
    if mode in ("operator", "operator_sync", "sync", ""):
        if tenant_publishers and os.getenv("CMS_PUBLISH_MODE", "").strip() == "":
            # 配置了租户列表时默认走分租户发布（更可靠）
            if os.getenv("CMS_FORCE_OPERATOR_SYNC", "").strip() in ("1", "true", "yes"):
                return "operator_sync"
            return "per_tenant"
        return "operator_sync"
    raise RuntimeError(
        f"未知 CMS_PUBLISH_MODE={mode!r}，可用 per_tenant 或 operator_sync"
    )


def load_settings(*, require_cms: bool = True) -> Settings:
    email_user = _require("EMAIL_USER")
    email_password = _require("EMAIL_PASSWORD")
    imap_host = os.getenv("IMAP_HOST", "mail.myhexin.com").strip()
    imap_port = int(os.getenv("IMAP_PORT", "993"))
    mail_sender = os.getenv("MAIL_SENDER", "webdetect@myhexin.com").strip().lower()
    cms_base_url = os.getenv("CMS_BASE_URL", "https://prenewcms.wewecall.com:5443").rstrip("/")

    cms_dry_run = os.getenv("CMS_DRY_RUN", "").strip() in ("1", "true", "yes")
    tenant_publishers = _parse_tenant_publishers()
    publish_mode = resolve_publish_mode(tenant_publishers)

    if require_cms and not cms_dry_run:
        if publish_mode == "per_tenant" and tenant_publishers:
            cms_email = os.getenv("CMS_EMAIL", "").strip()
            cms_password = os.getenv("CMS_PASSWORD", "").strip()
        else:
            cms_email = _require("CMS_EMAIL")
            cms_password = _require("CMS_PASSWORD")
    else:
        cms_email = os.getenv("CMS_EMAIL", "").strip()
        cms_password = os.getenv("CMS_PASSWORD", "").strip()

    if require_cms and not cms_dry_run and publish_mode == "per_tenant":
        if not tenant_publishers:
            raise RuntimeError(
                "CMS_PUBLISH_MODE=per_tenant 但未配置 CMS_TENANT_PUBLISHERS"
            )

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
        publish_mode=publish_mode,
        tenant_publishers=tenant_publishers,
    )
