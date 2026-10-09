"""仅测试 IMAP 收信（不登录 CMS）。用法: python -m src.test_imap"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import load_settings
from fetch_emails import fetch_latest_by_keywords

KEYWORDS = ("贵金属周报", "外汇周报")


def main() -> int:
    settings = load_settings(require_cms=False)
    mails = fetch_latest_by_keywords(settings, KEYWORDS)
    for m in mails:
        preview = m.body_text[:200].replace("\n", " ")
        print(f"[{m.keyword}] {m.subject}")
        print(f"  时间: {m.date.isoformat()}  字数: {len(m.body_text)}")
        print(f"  预览: {preview}…")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"错误: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
