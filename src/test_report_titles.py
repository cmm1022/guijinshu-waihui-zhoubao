"""标题日期区间（上周一～上周五）回归用例。"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_titles import format_report_title, last_monday_friday

PRECIOUS = "贵金属周报"


def _legacy_wrong_range(run: date) -> tuple[date, date]:
    """修复前：UTC date.today() 在北京周一清晨仍为周日时的错误区间。"""
    wd = run.weekday()
    task_mon = run if wd == 0 else run - timedelta(days=wd)
    return task_mon - timedelta(days=7), task_mon - timedelta(days=3)


def main() -> int:
    # 北京 10/19 07:00 触发时，UTC 仍可能是 10/18（周日）→ 旧逻辑会得到 10/05~10/09
    legacy = _legacy_wrong_range(date(2026, 10, 18))
    assert legacy == (date(2026, 10, 5), date(2026, 10, 9)), legacy

    cases = [
        (date(2026, 10, 19), (date(2026, 10, 12), date(2026, 10, 16))),  # 周一
        (date(2026, 10, 18), (date(2026, 10, 12), date(2026, 10, 16))),  # UTC 周日→对齐周一
        (date(2026, 10, 17), (date(2026, 10, 12), date(2026, 10, 16))),  # 周六
    ]
    failed = 0
    for run, want in cases:
        got = last_monday_friday(run)
        title = format_report_title(PRECIOUS, run)
        ok = got == want
        if not ok:
            failed += 1
        print(f"{run} -> {got} {title} {'OK' if ok else 'FAIL want ' + str(want)}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
