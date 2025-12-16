from pydantic import BaseModel

class DashboardOut(BaseModel):
    date_key: str
    total_collected_amount: float
    total_collected_water: float
    total_collected_electric: float
    collected_rooms: int
    uncollected_rooms: int
