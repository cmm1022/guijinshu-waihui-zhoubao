"""调试 CMS 登录（保存截图，不发布）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings

OUT = Path(__file__).resolve().parent.parent / "artifacts"


def main() -> int:
    settings = load_settings()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        page.goto(f"{settings.cms_base_url}/login", wait_until="networkidle", timeout=120_000)
        page.get_by_role("tab", name="密码登录").click()
        page.get_by_role("textbox", name="邮箱").fill(settings.cms_email)
        page.get_by_role("textbox", name="密码").fill(settings.cms_password)
        page.screenshot(path=str(OUT / "cms_before_login.png"))
        page.get_by_role("button", name="立即登录").click()
        page.wait_for_timeout(5000)
        page.screenshot(path=str(OUT / "cms_after_login_attempt.png"), full_page=True)
        print("URL:", page.url)
        body = page.locator("body").inner_text()[:500]
        print("Body snippet:", body.replace("\n", " ")[:300])
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
