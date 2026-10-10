"""探测内容同步下拉全部选项文案（找杭州银行等准确名称）。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from playwright.sync_api import sync_playwright

from config import load_settings
from publish_cms import _browser_context, _editor_row, _login, _open_editor_direct, _scroll_to_basic_info


def main() -> int:
    settings = load_settings()
    out = Path(__file__).resolve().parent.parent / "artifacts" / "sync_all_labels.txt"
    with sync_playwright() as p:
        browser, ctx = _browser_context(p, settings, headless=True)
        page = ctx.new_page()
        _login(page, settings)
        _open_editor_direct(page, settings)
        _scroll_to_basic_info(page)
        row = _editor_row(page, "内容同步")
        row.locator(".antd-editor-select-selector").click()
        page.wait_for_timeout(800)
        dd = page.locator(".antd-editor-select-dropdown").locator("visible=true").last
        holder = dd.locator(".rc-virtual-list-holder").first
        seen: set[str] = set()
        for _ in range(250):
            for t in dd.locator(".antd-editor-select-item-option-content").all_inner_texts():
                t = t.strip()
                if t:
                    seen.add(t)
            if holder.count():
                holder.evaluate("el => { el.scrollTop += 150; }")
            page.wait_for_timeout(80)
        lines = sorted(seen)
        out.write_text("\n".join(lines), encoding="utf-8")
        print("total", len(lines), "written", out)
        for x in lines:
            if "杭州" in x or "浙江" in x:
                print(repr(x))
        browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
