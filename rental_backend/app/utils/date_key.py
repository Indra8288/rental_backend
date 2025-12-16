from datetime import date , datetime

def to_date_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"

def prev_month_key(date_key: str) -> str:
    # date_key = "YYYY-MM"
    d = datetime.strptime(date_key + "-01", "%Y-%m-%d")
    year = d.year
    month = d.month - 1
    if month == 0:
        month = 12
        year -= 1
    return f"{year:04d}-{month:02d}"