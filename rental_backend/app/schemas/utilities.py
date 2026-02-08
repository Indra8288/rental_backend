from __future__ import annotations
from pydantic import Field
from app.schemas.common import APIModel

# Single-create payloads
class ElectricCreate(APIModel):
    room_id: str
    current_num: int = Field(ge=0)
    price_khr: float = Field(ge=0)

class WaterCreate(APIModel):
    room_id: str
    current_num: int = Field(ge=0)

# Bulk payloads
class ElectricBulkItem(APIModel):
    room_id: str
    current_num: int = Field(ge=0)
    price_khr: float = Field(ge=0)

class WaterBulkItem(APIModel):
    room_id: str
    current_num: int = Field(ge=0)

class ElectricBulkCreate(APIModel):
    items: list[ElectricBulkItem]

class WaterBulkCreate(APIModel):
    items: list[WaterBulkItem]

# Frontend overview
class UtilityRoomOverview(APIModel):
    room_id: str
    room_no: str
    prev_num: int | None = None
    current_num: int | None = None
    total_khr: float | None = None

class UtilitiesOverviewOut(APIModel):
    house_id: int
    date_key: str
    utility_type: str  # "water" | "electric"
    rooms: list[UtilityRoomOverview]
