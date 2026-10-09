"""周报标题日期区间与简介生成。"""

from __future__ import annotations

import os
from datetime import date, datetime, timedelta

from market_review_summary import summarize_market_review


def _parse_run_date() -> date:
    raw = os.getenv("RUN_DATE", "").strip()
    if raw:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    return date.today()


def _task_monday(run: date) -> date:
    """定时为每周一；非周一手动试跑时，按「本周一」作为任务日推算区间。"""
    if run.weekday() == 0:
        return run
    return run - timedelta(days=run.weekday())


def last_monday_friday(run_date: date | None = None) -> tuple[date, date]:
    """每周一 9:00：标题区间为该周一对应的「上周一 ~ 上周五」。"""
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
