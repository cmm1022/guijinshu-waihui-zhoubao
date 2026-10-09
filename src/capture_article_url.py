"""headed 一次：记录「发布 → 文章」后的编辑页 URL。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import _login

OUT = Path(__file__).resolve().parent.parent / "artifacts"


def main() -> int:
    settings = load_settings()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        _login(page, settings)
        page.wait_for_selector("text=内容列表", timeout=60_000)
        page.wait_for_selector(".ant-btn:has-text('发布')", timeout=60_000)

        urls: list[str] = []

        def on_nav(frame):
            if frame == page.main_frame:
                urls.append(page.url)

        page.on("framenavigated", on_nav)
        page.locator(".ant-btn").filter(has_text="发布").last.click(timeout=15_000)
        page.wait_for_selector(".ant-dropdown-menu-item:has-text('文章')", timeout=10_000)
        page.locator(".ant-dropdown-menu-item").filter(has_text="文章").first.click()
        page.wait_for_timeout(8_000)

        url = page.url
        (OUT / "new_article_url.txt").write_text(url, encoding="utf-8")
        (OUT / "nav_urls.txt").write_text("\n".join(urls), encoding="utf-8")
        page.screenshot(path=str(OUT / "cms_editor.png"), full_page=True)
        print("NEW_ARTICLE_URL=", url)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
