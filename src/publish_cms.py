"""登录内容管理平台并发布文章（Playwright）。"""

from __future__ import annotations

import json
import os
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from playwright.sync_api import BrowserContext, Page, sync_playwright

from config import Settings

DEFAULT_EDITOR_PATH = "/editor/publish-home?pulishType=ARTICLE&back=contentList"

PRECIOUS_METAL = "贵金属周报"
FOREX = "外汇周报"

# CMS 发布接口 otherTenantIds（与下拉展示名不同，见 probe_full_publish_posts 抓包）
_PUBLISH_TENANT_IDS: dict[str, list[str]] = {
    PRECIOUS_METAL: ["zrcub", "psbc", "hzbank"],  # 浙江省联社、邮储银行、杭州银行
    FOREX: ["bocom", "bocom"],  # 两个「交通银行」租户
}
_PUBLISH_API_SUFFIX = "/hcc/manager/v1/content/publish"


@dataclass
class ArticleDraft:
    title: str
    body: str
    keyword: str
    summary: str | None = None
    body_html: str | None = None


def _login(page: Page, settings: Settings) -> None:
    login_url = f"{settings.cms_base_url}/login"
    page.goto(login_url, wait_until="domcontentloaded", timeout=120_000)
    pwd_tab = page.get_by_role("tab", name="密码登录")
    pwd_tab.wait_for(state="visible", timeout=30_000)
    if pwd_tab.get_attribute("aria-selected") != "true":
        pwd_tab.click(force=True)
    email_box = page.get_by_role("textbox", name="邮箱")
    email_box.first.wait_for(state="visible", timeout=15_000)
    email_box.first.fill(settings.cms_email)
    page.get_by_role("textbox", name="密码").fill(settings.cms_password)
    page.get_by_role("button", name="立即登录").click()
    try:
        page.wait_for_url(re.compile(r"/base/content-list|/base/|/editor/"), timeout=60_000)
    except Exception as exc:
        if "/login" in page.url:
            raise RuntimeError(
                "CMS 登录失败，仍停留在登录页，请检查 CMS_EMAIL / CMS_PASSWORD"
            ) from exc
        raise
    page.wait_for_load_state("networkidle", timeout=120_000)


def _editor_url(settings: Settings) -> str:
    custom = os.getenv("CMS_EDITOR_URL", "").strip()
    if custom:
        return custom if custom.startswith("http") else f"{settings.cms_base_url}{custom}"
    path = os.getenv("CMS_NEW_ARTICLE_PATH", DEFAULT_EDITOR_PATH).strip()
    if path.startswith("http"):
        return path
    if not path.startswith("/"):
        path = "/" + path
    return f"{settings.cms_base_url}{path}"


def _open_editor_direct(page: Page, settings: Settings) -> None:
    page.goto(_editor_url(settings), wait_until="networkidle", timeout=180_000)
    if "/login" in page.url:
        raise RuntimeError("打开编辑页时被重定向到登录页，请检查 CMS 会话")
    _wait_for_editor(page)


def _wait_for_editor(page: Page) -> None:
    page.wait_for_url(re.compile(r"/editor/publish-home"), timeout=60_000)
    try:
        page.wait_for_selector(
            "textarea[placeholder*='标题'], input[placeholder*='标题']",
            timeout=90_000,
        )
    except Exception:
        page.get_by_text("从这里开始写正文").first.wait_for(state="visible", timeout=30_000)
    page.wait_for_timeout(800)


def _scroll_to_basic_info(page: Page) -> None:
    page.keyboard.press("End")
    page.wait_for_timeout(800)
    src = page.get_by_placeholder("请输入内容来源")
    src.scroll_into_view_if_needed()
    src.wait_for(state="visible", timeout=120_000)


def _open_editor_select(page: Page, index: int) -> None:
    page.locator("[class*='editor-select']").nth(index).scroll_into_view_if_needed()
    page.locator("[class*='editor-select']").nth(index).click(timeout=15_000)


def _pick_dropdown_option(page: Page, option: str) -> None:
    page.wait_for_timeout(300)
    lists = page.locator(".rc-virtual-list, .antd-editor-select-dropdown")
    for i in range(lists.count()):
        block = lists.nth(i)
        if not block.is_visible():
            continue
        hit = block.get_by_text(option, exact=True)
        if hit.count() > 0:
            hit.first.click(timeout=10_000)
            return
    raise RuntimeError(f"下拉中未找到选项: {option}")


def _editor_row(page: Page, label: str):
    return page.locator(".antd-editor-row").filter(has_text=label).first


def _select_root(page: Page, field_id: str):
    box = page.locator(f"#{field_id}")
    box.scroll_into_view_if_needed()
    return box.locator(
        'xpath=ancestor::div[contains(@class,"antd-editor-select")][last()]'
    )


def _select_current_label(select_root) -> str:
    items = select_root.locator(".antd-editor-select-selection-item")
    if items.count() > 0:
        return (items.first.inner_text() or "").strip()
    return ""


def _sync_dropdown(page: Page):
    dd = page.locator(".antd-editor-select-dropdown").locator("visible=true").last
    dd.wait_for(state="visible", timeout=10_000)
    return dd, dd.locator(".rc-virtual-list-holder").first


def _virtual_list_scroll_top(holder) -> None:
    if holder.count() > 0:
        holder.evaluate("el => { el.scrollTop = 0; }")


def _click_option_in_open_dropdown(page: Page, option: str) -> None:
    """虚拟下拉滚动直到出现选项并点击（不支持输入筛选）。"""
    dd, holder = _sync_dropdown(page)
    _virtual_list_scroll_top(holder)
    page.wait_for_timeout(150)
    for _ in range(120):
        item = dd.locator(".antd-editor-select-item-option-content").get_by_text(
            option, exact=True
        )
        if item.count() > 0:
            item.first.click(timeout=5_000)
            return
        if holder.count() > 0:
            holder.evaluate("el => { el.scrollTop += 120; }")
        else:
            dd.evaluate(
                """() => {
                    const root = document.querySelector(
                      '.antd-editor-select-dropdown:not([style*="display: none"])'
                    );
                    const list = root && root.querySelector('.rc-virtual-list-holder');
                    if (list) list.scrollTop += 120;
                }"""
            )
        page.wait_for_timeout(120)
    raise RuntimeError(f"下拉列表中未找到: {option}")


def _select_channel_ths(page: Page) -> None:
    root = _select_root(page, "form_item_channelPlatform")
    if _select_current_label(root) == "同花顺":
        return
    trigger = page.locator("#form_item_channelPlatform").locator(
        'xpath=ancestor::div[contains(@class,"antd-editor-select-selector")][1]'
    )
    trigger.click(timeout=10_000)
    page.wait_for_timeout(400)
    _click_option_in_open_dropdown(page, "同花顺")
    page.wait_for_timeout(300)
    if _select_current_label(root) != "同花顺":
        raise RuntimeError("渠道平台未能选定为「同花顺」")


def _fill_basic_fields(page: Page, draft: ArticleDraft) -> None:
    _scroll_to_basic_info(page)
    page.get_by_placeholder("请输入内容来源").fill("同花顺")
    # 基本信息区下拉顺序：0=数据类型，1=渠道平台（见 artifacts/inputs.json）
    _select_channel_ths(page)
    page.get_by_text("无图", exact=True).click()
    if draft.keyword == PRECIOUS_METAL and draft.summary:
        page.get_by_placeholder("请输入简介").fill(draft.summary)


def _sync_select_root(page: Page):
    return _select_root(page, "form_item_otherTenantIds")


def _sync_trigger(page: Page):
    return page.locator("#form_item_otherTenantIds").locator(
        'xpath=ancestor::div[contains(@class,"antd-editor-select-selector")][1]'
    )


def _count_sync_selected(row, name: str) -> int:
    items = row.locator(".antd-editor-select-selection-item")
    n = 0
    for i in range(items.count()):
        if (items.nth(i).inner_text() or "").strip() == name:
            n += 1
    return n


def _close_dropdown_focus_basic(page: Page) -> None:
    """收起下拉；勿点标题（会滚到页顶，易导致基本信息区状态异常）。"""
    page.get_by_placeholder("请输入内容来源").click(timeout=5_000)
    page.wait_for_timeout(350)


def _click_unselected_sync_option(page: Page, option: str) -> None:
    """在 #form_item_otherTenantIds 对应下拉里滚动并点击未选中项。"""
    ok = page.evaluate(
        """(label) => {
          const listRoot = document.getElementById('form_item_otherTenantIds_list')
            || document.querySelector('[id^="form_item_otherTenantIds_list"]');
          const scope = listRoot
            ? (listRoot.closest('.antd-editor-select-dropdown') || listRoot.parentElement)
            : null;
          const dd = scope || document.querySelector(
            '.antd-editor-select-dropdown:not([style*="display: none"])'
          );
          if (!dd) return false;
          const holder = dd.querySelector('.rc-virtual-list-holder');
          if (holder) holder.scrollTop = 0;
          const norm = (s) => (s || '').replace(/\\s+/g, '').trim();
          const want = norm(label);
          for (let round = 0; round < 180; round++) {
            for (const opt of dd.querySelectorAll('.antd-editor-select-item-option')) {
              if ((opt.className || '').includes('option-selected')) continue;
              const t = opt.querySelector('.antd-editor-select-item-option-content');
              const text = t ? t.innerText.trim() : (opt.innerText || '').trim();
              if (norm(text) !== want) continue;
              (t || opt).dispatchEvent(new MouseEvent('mousedown', { bubbles: true }));
              (t || opt).click();
              return true;
            }
            if (holder) holder.scrollTop += 120;
          }
          return false;
        }""",
        option,
    )
    if not ok:
        dd, holder = _sync_dropdown(page)
        _virtual_list_scroll_top(holder)
        page.wait_for_timeout(150)
        for _ in range(120):
            options = dd.locator(".antd-editor-select-item-option")
            for i in range(options.count()):
                opt_el = options.nth(i)
                label_el = opt_el.locator(".antd-editor-select-item-option-content")
                text = (
                    label_el.first.inner_text()
                    if label_el.count()
                    else opt_el.inner_text()
                ).strip()
                if text.replace(" ", "") != option.replace(" ", ""):
                    continue
                cls = opt_el.get_attribute("class") or ""
                if "item-option-selected" in cls:
                    continue
                opt_el.click(timeout=5_000)
                page.wait_for_timeout(500)
                return
            if holder.count() > 0:
                holder.evaluate("el => { el.scrollTop += 120; }")
            page.wait_for_timeout(120)
        raise RuntimeError(f"内容同步列表中未找到可勾选的: {option}")
    page.wait_for_timeout(500)


def _list_sync_tags(row) -> list[str]:
    items = row.locator(".antd-editor-select-selection-item")
    return [(items.nth(i).inner_text() or "").strip() for i in range(items.count())]


def _assert_sync_selected(row, needed: Counter[str]) -> None:
    tags = _list_sync_tags(row)
    tag_counter = Counter(tags)
    missing = []
    for name, count in needed.items():
        if tag_counter[name] < count:
            missing.append(f"{name}(需{count}有{tag_counter[name]})")
    if missing:
        raise RuntimeError(f"内容同步未完成: {', '.join(missing)}；当前标签={tags}")


def _fill_content_sync(page: Page, needed: Counter[str]) -> None:
    """内容同步：form_item_otherTenantIds，多选下拉滚动勾选。"""
    row = _sync_select_root(page)
    row.scroll_into_view_if_needed()
    trigger = _sync_trigger(page)
    names = list(needed.keys())
    for name, count in needed.items():
        while _count_sync_selected(row, name) < count:
            trigger.click(timeout=10_000)
            page.wait_for_timeout(500)
            _click_unselected_sync_option(page, name)
            page.wait_for_timeout(400)
            if name != names[-1]:
                _close_dropdown_focus_basic(page)
    _close_dropdown_focus_basic(page)
    _assert_sync_selected(row, needed)


def _apply_content_sync_before_publish(page: Page, draft: ArticleDraft) -> None:
    """发布前最后勾选内容同步，避免填表/滚动冲掉已选项。"""
    needed = _sync_targets(draft)
    if not needed:
        return
    _scroll_to_basic_info(page)
    row = _sync_select_root(page)
    row.scroll_into_view_if_needed()
    for attempt in range(3):
        _fill_content_sync(page, needed)
        try:
            _assert_sync_selected(row, needed)
            return
        except RuntimeError:
            if attempt == 2:
                raise
            # 清空已选后重试（杭州银行偶发未写入表单）
            remove_btns = row.locator(".antd-editor-select-selection-item-remove")
            while remove_btns.count() > 0:
                remove_btns.first.click()
                page.wait_for_timeout(150)
            page.wait_for_timeout(300)


def _publish_tenant_ids(draft: ArticleDraft) -> list[str]:
    return list(_PUBLISH_TENANT_IDS.get(draft.keyword, []))


def _install_publish_tenant_guard(page: Page, draft: ArticleDraft) -> None:
    """发布请求兜底：强制写入 otherTenantIds，避免 UI 未绑定导致编辑页为空。"""
    expected = _publish_tenant_ids(draft)
    if not expected:
        return

    def _patch(route) -> None:
        req = route.request
        if req.method != "POST" or not req.url.endswith(_PUBLISH_API_SUFFIX):
            route.continue_()
            return
        try:
            payload = json.loads(req.post_data or "{}")
        except json.JSONDecodeError:
            route.continue_()
            return
        payload["otherTenantIds"] = expected
        route.continue_(post_data=json.dumps(payload, ensure_ascii=False))

    page.route(f"**{_PUBLISH_API_SUFFIX}", _patch)


def _sync_targets(draft: ArticleDraft) -> Counter[str]:
    if draft.keyword == PRECIOUS_METAL:
        # 杭州银行放在最后勾选，减少后续操作覆盖首项的情况
        return Counter({"浙江省联社": 1, "邮储银行": 1, "杭州银行": 1})
    if draft.keyword == FOREX:
        return Counter({"交通银行": 2})
    return Counter()


def _focus_body_editor(page: Page):
    for sel in (
        ".ProseMirror[contenteditable='true']",
        "[contenteditable='true']",
        "[data-slate-editor='true']",
    ):
        loc = page.locator(sel)
        for i in range(loc.count()):
            box = loc.nth(i)
            try:
                if not box.is_visible():
                    continue
                box.click(timeout=5_000)
                return box
            except Exception:
                continue
    hint = page.get_by_text(re.compile(r"从这里开始写正文"))
    hint.first.click(timeout=10_000)
    return page.locator(".ProseMirror, [contenteditable='true']").first


def _fill_body(page: Page, text: str, html: str | None = None) -> None:
    editor = _focus_body_editor(page)
    page.keyboard.press("Control+a")
    page.keyboard.press("Backspace")
    if html:
        page.evaluate(
            """async ({html, plain}) => {
                const item = new ClipboardItem({
                  'text/html': new Blob([html], {type: 'text/html'}),
                  'text/plain': new Blob([plain], {type: 'text/plain'}),
                });
                await navigator.clipboard.write([item]);
            }""",
            {"html": html, "plain": text},
        )
        page.keyboard.press("Control+v")
        page.wait_for_timeout(800)
        return
    try:
        editor.fill(text)
    except Exception:
        page.keyboard.insert_text(text)


def _fill_and_submit(page: Page, draft: ArticleDraft) -> None:
    title_loc = page.get_by_placeholder(re.compile(r"请在这里输入标题"))
    if title_loc.count() == 0:
        title_loc = page.locator("textarea").first
    title_loc.first.click()
    title_loc.first.fill(draft.title)

    _fill_body(page, draft.body, draft.body_html)

    _fill_basic_fields(page, draft)

    page.keyboard.press("End")
    page.wait_for_timeout(500)
    _apply_content_sync_before_publish(page, draft)
    _install_publish_tenant_guard(page, draft)

    def _click_exact_publish() -> None:
        page.evaluate(
            """() => {
                const norm = (s) => (s || '').replace(/\\s+/g, '').trim();
                const btn = [...document.querySelectorAll('button')]
                  .find(b => norm(b.innerText) === '发布'
                    && !b.classList.contains('ant-btn-fixtime'));
                if (!btn) throw new Error('未找到发布按钮');
                btn.click();
            }"""
        )

    _click_exact_publish()
    page.wait_for_timeout(5_000)


def _headless_default() -> bool:
    return os.getenv("CMS_HEADLESS", "1").strip() not in ("0", "false", "no")


def _browser_channel() -> str:
    return os.getenv("CMS_BROWSER_CHANNEL", "msedge").strip() or "msedge"


def _browser_context(p, settings: Settings, *, headless: bool | None = None):
    if headless is None:
        headless = _headless_default()
    launch_kwargs: dict = {
        "headless": headless,
        "channel": _browser_channel(),
    }
    args: list[str] = []
    if headless:
        args.append("--disable-blink-features=AutomationControlled")
    else:
        args.extend(["--start-maximized", "--disable-blink-features=AutomationControlled"])
    if args:
        launch_kwargs["args"] = args
    browser = p.chromium.launch(**launch_kwargs)
    if headless:
        context = browser.new_context(
            ignore_https_errors=True,
            viewport={"width": 1920, "height": 1080},
        )
    else:
        context = browser.new_context(ignore_https_errors=True, no_viewport=True)
    origin = settings.cms_base_url.rstrip("/")
    try:
        context.grant_permissions(
            ["clipboard-read", "clipboard-write"],
            origin=origin,
        )
    except Exception:
        pass
    return browser, context


def publish_many(settings: Settings, drafts: list[ArticleDraft]) -> None:
    if settings.cms_dry_run:
        for d in drafts:
            print(f"[DRY RUN] {d.title!r} sync={_sync_targets(d)}")
        return

    with sync_playwright() as p:
        browser, context = _browser_context(p, settings)
        list_page = context.new_page()
        try:
            _login(list_page, settings)
            for draft in drafts:
                _open_editor_direct(list_page, settings)
                _fill_and_submit(list_page, draft)
                print(f"已提交发布: {draft.title}")
        finally:
            browser.close()
