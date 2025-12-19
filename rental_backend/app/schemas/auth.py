from app.schemas.common import APIModel

class Token(APIModel):
    access_token: str
    token_type: str = "bearer"
