"""标题日期区间（上周一～上周五）回归用例。"""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from report_titles import format_report_title, last_monday_friday

PRECIOUS = "贵金属周报"


def main() -> int:
    cases = [
        (date(2026, 10, 19), (date(2026, 10, 12), date(2026, 10, 16))),  # 周一
        (date(2026, 10, 18), (date(2026, 10, 12), date(2026, 10, 16))),  # 周日
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
