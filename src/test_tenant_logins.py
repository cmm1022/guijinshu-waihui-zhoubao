"""验证 CMS_TENANT_PUBLISHERS 各账号能否登录并打开新建文章页。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import (
    _launch_browser,
    _login,
    _new_browser_context,
    _open_editor_direct,
)


def main() -> int:
    settings = load_settings()
    if not settings.tenant_publishers:
        print("未配置 CMS_TENANT_PUBLISHERS")
        return 1
    failed = 0
    with sync_playwright() as p:
        browser = _launch_browser(p, settings, headless=True)
        try:
            for tenant in settings.tenant_publishers:
                context = _new_browser_context(browser, settings)
                page = context.new_page()
                try:
                    _login(
                        page,
                        settings,
                        email=tenant.email,
                        password=tenant.password,
                    )
                    print(f"[登录 OK] {tenant.name} -> {page.url}")
                    _open_editor_direct(page, settings)
                    print(f"[编辑页 OK] {tenant.name} -> {page.url}")
                except Exception as exc:
                    failed += 1
                    print(f"[失败] {tenant.name}: {exc}")
                finally:
                    context.close()
        finally:
            browser.close()
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
