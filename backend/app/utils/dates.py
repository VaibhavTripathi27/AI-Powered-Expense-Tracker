from __future__ import annotations

import calendar
from datetime import date, timedelta
from typing import Tuple


def month_range(year: int, month: int) -> Tuple[date, date]:
    start = date(year, month, 1)
    last_day = calendar.monthrange(year, month)[1]
    end = date(year, month, last_day)
    return start, end


def current_month_range(today: date | None = None) -> Tuple[date, date]:
    today = today or date.today()
    return month_range(today.year, today.month)


def previous_month_range(today: date | None = None) -> Tuple[date, date]:
    today = today or date.today()
    first_of_this_month = date(today.year, today.month, 1)
    last_of_prev = first_of_this_month - timedelta(days=1)
    return month_range(last_of_prev.year, last_of_prev.month)


def last_n_months(n: int, today: date | None = None) -> list[Tuple[int, int]]:
    """Return [(year, month), ...] for the trailing n months, oldest first."""
    today = today or date.today()
    months: list[Tuple[int, int]] = []
    year, month = today.year, today.month
    for _ in range(n):
        months.append((year, month))
        month -= 1
        if month == 0:
            month = 12
            year -= 1
    return list(reversed(months))