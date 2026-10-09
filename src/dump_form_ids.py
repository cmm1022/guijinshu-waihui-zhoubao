"""登录编辑页后打印所有 form_item_* 的 id（便于配置内容同步）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import _browser_context, _login, _open_editor_direct, _scroll_to_basic_info

with sync_playwright() as p:
    from config import load_settings

    browser, context = _browser_context(p, load_settings())
    page = context.new_page()
    settings = load_settings()
    _login(page, settings)
    _open_editor_direct(page, settings)
    _scroll_to_basic_info(page)
    ids = page.evaluate(
        """() => [...document.querySelectorAll('[id^="form_item"]')]
          .map(el => ({ id: el.id, tag: el.tagName, role: el.getAttribute('role') || '' }))"""
    )
    for row in ids:
        print(row)
    browser.close()
