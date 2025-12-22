from app.schemas.common import APIModel

class HouseCreate(APIModel):
    house_name: str

class HouseOut(APIModel):
    house_id: int
    house_name: str
    owner_id: int

class HouseUpdate(APIModel):
    house_name: str
