from datetime import date, datetime

def to_date_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"

def prev_month_key(date_key: str) -> str:
    d = datetime.strptime(date_key + "-01", "%Y-%m-%d")
    year = d.year
    month = d.month - 1
    if month == 0:
        month = 12
        year -= 1
    return f"{year:04d}-{month:02d}"

def make_room_id(house_id: int, room_no: str) -> str:
    return f"{house_id}:{room_no}"
