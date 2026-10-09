"""根据「行情回顾」段落撰写 CMS 简介（≤60 字，非原文截取）。"""

from __future__ import annotations

import re


def extract_market_review_section(body: str) -> str:
    for pat in (
        r"【\s*行情回顾\s*】([\s\S]*?)(?=【|$)",
        r"行情回顾[】\]]?\s*([\s\S]*?)(?=【|\n\n|$)",
    ):
        m = re.search(pat, body)
        if m:
            return m.group(1).strip()
    return ""


def _parse_change_pct(section: str, asset_pattern: str) -> float | None:
    m = re.search(
        rf"{asset_pattern}.{{0,220}}?涨跌幅为\s*([+-]?\d+(?:\.\d+)?)\s*%",
        section,
        re.DOTALL,
    )
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


def _chg_phrase(pct: float) -> str:
    if pct > 0:
        return f"周涨{ _fmt_num(abs(pct))}%"
    if pct < 0:
        return f"周跌{ _fmt_num(abs(pct))}%"
    return "持平"


def _fmt_num(x: float) -> str:
    s = f"{x:g}"
    return s


def _domestic_tail(sh_gold: float | None, sh_silver: float | None) -> str:
    if sh_gold is None or sh_silver is None:
        return ""
    if sh_gold > 0 and sh_silver > 0:
        return "，国内沪金沪银跟涨"
    if sh_gold < 0 and sh_silver < 0:
        return "，国内沪金沪银跟跌"
    if sh_gold == 0 and sh_silver == 0:
        return ""
    return "，国内沪金沪银走势分化"


def _headline(gold: float | None, silver: float | None) -> str:
    ints = [p for p in (gold, silver) if p is not None]
    if not ints:
        return "上周贵金属市场"
    if all(p > 0 for p in ints):
        return "上周贵金属价格走强"
    if all(p < 0 for p in ints):
        return "上周贵金属价格回落"
    if all(p == 0 for p in ints):
        return "上周贵金属价格震荡"
    return "上周贵金属走势分化"


def _fit_length(text: str, max_len: int) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    # 优先去掉 domestic 从句
    for sep in ("，国内", "；国内"):
        if sep in text:
            short = text.split(sep, 1)[0] + "。"
            if len(short) <= max_len:
                return short
    if text.endswith("。"):
        text = text[:-1]
    return text[: max_len - 1] + "…"


def summarize_market_review(body: str, max_len: int = 60) -> str:
    section = extract_market_review_section(body)
    if not section:
        fallback = re.sub(r"\s+", "", body.strip())
        return fallback[:max_len] if fallback else ""

    gold = _parse_change_pct(section, r"伦敦金现?")
    silver = _parse_change_pct(section, r"伦敦银现?")
    sh_gold = _parse_change_pct(section, r"沪金.*?主力合约")
    if sh_gold is None:
        sh_gold = _parse_change_pct(section, r"沪金")
    sh_silver = _parse_change_pct(section, r"沪银.*?主力合约")
    if sh_silver is None:
        sh_silver = _parse_change_pct(section, r"沪银")

    parts: list[str] = [_headline(gold, silver)]
    detail: list[str] = []
    if gold is not None:
        detail.append(f"伦敦金{_chg_phrase(gold)}")
    if silver is not None:
        detail.append(f"伦敦银{_chg_phrase(silver)}")
    if detail:
        parts.append("，" + "、".join(detail))
    parts.append(_domestic_tail(sh_gold, sh_silver))
    summary = "".join(parts)
    if not summary.endswith("。"):
        summary += "。"
    return _fit_length(summary, max_len)
