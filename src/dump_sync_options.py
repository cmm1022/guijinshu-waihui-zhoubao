import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import _browser_context, _editor_row, _login, _open_editor_direct, _scroll_to_basic_info

with sync_playwright() as p:
    from config import load_settings

    browser, context = _browser_context(p, load_settings())
    page = context.new_page()
    s = load_settings()
    _login(page, s)
    _open_editor_direct(page, s)
    _scroll_to_basic_info(page)
    row = _editor_row(page, "内容同步")
    row.locator(".antd-editor-select-selector").click()
    page.wait_for_timeout(1000)
    texts = page.evaluate(
        """() => [...document.querySelectorAll('[id^="form_item_otherTenantIds_list"]')]
          .map(x => x.innerText.trim()).filter(Boolean)"""
    )
    Path("artifacts/sync_options.txt").write_text("\n".join(texts), encoding="utf-8")
    print("count", len(texts))
    for t in texts[:30]:
        print(t)
    browser.close()
