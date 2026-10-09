"""登录 → 编辑页 → 填标题正文 → 打印 DOM 里是否有「内容基本信息/内容来源」。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import (
    _browser_context,
    _fill_body,
    _login,
    _open_editor_direct,
    _wait_for_editor,
)

OUT = Path(__file__).resolve().parent.parent / "artifacts"


def main() -> int:
    settings = load_settings()
    OUT.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser, context = _browser_context(p, settings)
        page = context.new_page()
        _login(page, settings)
        _open_editor_direct(page, settings)
        page.get_by_placeholder("请在这里输入标题").first.fill("测试标题")
        _fill_body(page, "测试正文一行")
        page.keyboard.press("End")
        page.wait_for_timeout(3000)
        info = page.evaluate(
            """() => ({
              url: location.href,
              hasBasic: document.body.innerText.includes('内容基本信息'),
              hasSource: document.body.innerText.includes('内容来源'),
              formItems: document.querySelectorAll('.ant-form-item').length,
              labels: [...document.querySelectorAll('.ant-form-item-label')]
                .map(x => x.textContent.trim()).slice(0, 15),
            })"""
        )
        page.screenshot(path=str(OUT / "debug_after_body.png"), full_page=True)
        print(info)
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
