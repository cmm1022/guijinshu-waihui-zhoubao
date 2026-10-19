"""周报标题日期区间与简介生成。"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

from market_review_summary import summarize_market_review

DEFAULT_TZ = "Asia/Shanghai"


def _report_tz() -> ZoneInfo:
    name = os.getenv("REPORT_TZ", DEFAULT_TZ).strip() or DEFAULT_TZ
    return ZoneInfo(name)


def _parse_run_date() -> date:
    raw = os.getenv("RUN_DATE", "").strip()
    if raw:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    return datetime.now(_report_tz()).date()


def _task_monday(run: date) -> date:
    """推算「本次定时任务对应的周一」。

    - 周一：任务日即当天。
    - 周六、周日：按即将执行的周一 9:00 批次（与周一跑同一标题区间），避免周日 UTC 触发时落到上上周。
    - 周二～周五：手动试跑，按所在自然周的周一。
    """
    wd = run.weekday()
    if wd == 0:
        return run
    if wd == 6:
        return run + timedelta(days=1)
    if wd == 5:
        return run + timedelta(days=2)
    return run - timedelta(days=wd)


def last_monday_friday(run_date: date | None = None) -> tuple[date, date]:
    """任务周一 9:00（北京时间）：标题为「上周一 ~ 上周五」。"""
    run = run_date or _parse_run_date()
    task_mon = _task_monday(run)
    monday = task_mon - timedelta(days=7)
    friday = task_mon - timedelta(days=3)
    return monday, friday


def format_report_title(keyword: str, run_date: date | None = None) -> str:
    mon, fri = last_monday_friday(run_date)
    fmt = lambda d: f"{d.year}/{d.month:02d}/{d.day:02d}"
    return f"{keyword}（{fmt(mon)}-{fmt(fri)}）"


def summary_from_market_review(body: str, max_len: int = 60) -> str:
    """根据「行情回顾」归纳撰写简介（≤60 字）。"""
    return summarize_market_review(body, max_len=max_len)
