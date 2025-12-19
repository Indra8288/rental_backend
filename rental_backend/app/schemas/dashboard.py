from app.schemas.common import APIModel

class DashboardOut(APIModel):
    house_id: int
    date_key: str
    total_collected_usd: float
    total_water_khr: float
    total_elect_khr: float
    collected_rooms: int
    uncollected_rooms: int
