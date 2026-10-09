"""登录后探测「发布 → 文章」控件。"""

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
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        _login(page, settings)
        page.screenshot(path=str(OUT / "cms_content_list.png"), full_page=True)
        print("URL:", page.url)
        for sel in ("button", "a", "[role=button]"):
            els = page.locator(sel)
            n = min(els.count(), 30)
            for i in range(n):
                t = els.nth(i).inner_text(timeout=1000) if els.nth(i).is_visible() else ""
                if t and len(t.strip()) < 20:
                    print(f"{sel}[{i}]: {t.strip()!r}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
