import calendar
from datetime import datetime, timedelta, date


def str_to_bool(value) -> bool:
    if isinstance(value, bool):  # Already a boolean
        return value
    if not isinstance(value, str):  # Handles None and non-string values
        return False
    return value.strip().lower() in {"true", "1", "yes"}


def get_last_date_of_week(year: int, week: int) -> datetime:
    """
    Returns the last date (Sunday) of a given ISO week and year.

    """
    # ISO weeks start on Monday, and week 1 is the week with the first Thursday of the year
    first_week_start = datetime.fromisocalendar(
        year, week, 1
    )  # Get Monday of the given week
    last_date = first_week_start + timedelta(days=6)  # Sunday of that week
    return last_date


def get_first_date_of_current_month() -> date:
    """
    Returns the first date of a given month and year.

    """
    today = datetime.today()
    return datetime(today.year, month=today.month, day=1).date()


def get_last_date_of_current_month() -> date:
    """
    Returns the last date of a current month and year.

    """
    today = datetime.today()
    return datetime(
        today.year,
        month=today.month,
        day=calendar.monthrange(today.year, today.month)[1],
    ).date()
