from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

def get_date_range():
    today = datetime.now(ZoneInfo("America/New_York")).date()
    current_month_start = today.replace(day=1)
    previous_month = current_month_start.month - 1 or 12
    previous_year = current_month_start.year if current_month_start.month > 1 else current_month_start.year - 1
    previous_month_start = current_month_start.replace(
        year=previous_year,
        month=previous_month,
    )
    # return f"2026-07-01T00:00:00", f"2026-08-01T00:00:00"
    return f"{previous_month_start}T00:00:00", f"{current_month_start}T00:00:00"


def get_previous_month_date_range():
    today = datetime.now(ZoneInfo("America/New_York")).date()
    current_month_start = today.replace(day=1)
    previous_month = current_month_start.month - 1 or 12
    previous_year = current_month_start.year if current_month_start.month > 1 else current_month_start.year - 1
    previous_month_start = current_month_start.replace(
        year=previous_year,
        month=previous_month,
    )
    previous_month_end = current_month_start - timedelta(days=1)
    # return f"2026-07-01T00:00:00", f"2026-07-31T00:00:00"
    return f"{previous_month_start}T00:00:00", f"{previous_month_end}T00:00:00"

def get_fiscal_year_range():
    today = datetime.now(ZoneInfo("America/New_York")).date()
    fiscal_year_start_year = today.year
    if today < datetime(today.year, 7, 1, tzinfo=ZoneInfo("America/New_York")).date():
        fiscal_year_start_year -= 1

    fiscal_year_start = date(fiscal_year_start_year, 7, 1)
    last_day_of_last_month = today.replace(day=1) - timedelta(days=1)
    return f"{fiscal_year_start}T00%3A00%3A00Z", f"{last_day_of_last_month}T00%3A00%3A00Z"
