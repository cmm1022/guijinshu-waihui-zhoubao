"""登录 CMS 后保存截图与可见菜单文案，便于配置 CMS_NEW_ARTICLE_PATH。"""

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
        browser = p.chromium.launch(headless=False, channel="msedge")
        context = browser.new_context(ignore_https_errors=True)
        page = context.new_page()
        _login(page, settings)
        shot = OUT / "cms_after_login.png"
        page.screenshot(path=str(shot), full_page=True)
        print(f"当前 URL: {page.url}")
        print(f"截图: {shot}")
        texts = page.locator("a, button, span, div").all_inner_texts()
        sample = [t.strip() for t in texts if t and len(t.strip()) < 30][:40]
        print("页面短文本采样:", sample)
        input("已在浏览器中打开后台，请手动点进「新建文章」后按 Enter 结束…")
        print(f"最终 URL: {page.url}")
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
