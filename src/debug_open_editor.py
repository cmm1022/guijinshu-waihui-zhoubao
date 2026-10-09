from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import _ensure_content_list, _login

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
        _ensure_content_list(page, settings)
        page.locator(".ant-btn").filter(has_text="发布").last.click()
        page.wait_for_timeout(1000)
        item = page.locator(".ant-dropdown-menu:visible .ant-dropdown-menu-item").filter(
            has_text="文章"
        )
        print("visible menu 文章", item.count())
        try:
            with context.expect_page(timeout=8_000) as pinfo:
                item.first.click()
            new = pinfo.value
            new.wait_for_load_state("domcontentloaded")
            print("new tab URL", new.url)
            new.screenshot(path=str(OUT / "editor_new_tab.png"), full_page=True)
        except Exception as exc:
            print("no new tab", exc)
            item.first.click()
            page.wait_for_timeout(5_000)
            print("same tab URL", page.url)
            page.screenshot(path=str(OUT / "editor_same_tab.png"), full_page=True)
            print("frames", len(page.frames))
            for i, f in enumerate(page.frames):
                print(" frame", i, f.url[:80] if f.url else "")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
