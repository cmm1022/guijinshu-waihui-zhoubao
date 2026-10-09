from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import _login

CANDIDATES = [
    "/base/article/edit",
    "/base/content/article/edit",
    "/base/article/create",
    "/base/content-edit",
    "/base/article-add",
    "/base/publish/article",
]


def main() -> int:
    settings = load_settings()
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1920, "height": 1080},
        )
        page = context.new_page()
        _login(page, settings)
        for path in CANDIDATES:
            url = f"{settings.cms_base_url}{path}"
            page.goto(url, wait_until="domcontentloaded", timeout=30_000)
            page.wait_for_timeout(2000)
            title_inputs = page.locator(
                "input[placeholder*='标题'], textarea[placeholder*='标题']"
            ).count()
            print(path, "->", page.url, "title_fields", title_inputs)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
