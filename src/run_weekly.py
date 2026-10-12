"""每周任务入口：拉取两封周报邮件并发布到 CMS。"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import os

from config import load_settings
from fetch_emails import fetch_latest_by_keywords
from publish_cms import PRECIOUS_METAL, ArticleDraft, publish_many
from report_titles import format_report_title, summary_from_market_review

KEYWORDS = (PRECIOUS_METAL, "外汇周报")


def main() -> int:
    settings = load_settings()
    print(f"CMS 发布模式: {settings.publish_mode}")
    if settings.publish_mode == "per_tenant":
        print(
            "已配置租户: "
            + ", ".join(t.name for t in settings.tenant_publishers)
        )
    mails = fetch_latest_by_keywords(settings, KEYWORDS)
    drafts: list[ArticleDraft] = []
    for m in mails:
        title = format_report_title(m.keyword)
        summary = None
        if m.keyword == PRECIOUS_METAL:
            summary = summary_from_market_review(m.body_text)
        drafts.append(
            ArticleDraft(
                title=title,
                body=m.body_text,
                body_html=m.body_html,
                keyword=m.keyword,
                summary=summary,
            )
        )
        print(
            f"已匹配: [{m.keyword}] {m.subject} ({m.date.isoformat()})，"
            f"发布标题: {title}，正文 {len(m.body_text)} 字"
        )
        if summary:
            print(f"  简介: {summary}")
    only = os.getenv("PUBLISH_ONLY", "").strip()
    if only:
        drafts = [d for d in drafts if only in d.keyword]
        if not drafts:
            raise RuntimeError(f"PUBLISH_ONLY={only!r} 未匹配到草稿")
        print(f"（试跑模式：仅发布 {only}）")
    publish_many(settings, drafts)
    print("发布流程已执行完成。")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
