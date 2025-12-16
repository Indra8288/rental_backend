from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://postgres:postgres@localhost:5432/rental_db"

    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 12

    UPLOAD_DIR: str = "./uploads"

    SEED_OWNER_USERNAME: str = "owner"
    SEED_OWNER_PASSWORD: str = "owner1234"
    SEED_OWNER_ROLE: str = "owner"

settings = Settings()
