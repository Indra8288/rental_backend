from app.schemas.common import APIModel

class DashboardOut(APIModel):
    house_id: int
    date_key: str

    # Currency rule (v4.2):
    # - payments are stored/calculated in KHR internally (even if column name says *_usd)
    # - we expose both KHR and USD for convenience (USD derived by /4000)
    total_collected_khr: float
    total_collected_usd: float

    total_water_khr: float
    total_elect_khr: float
    collected_rooms: int
    uncollected_rooms: int
