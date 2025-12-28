from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    DATABASE_URL: str = "postgresql+psycopg2://rental_user:CHANGE_ME@localhost:5432/rental_db"
    JWT_SECRET: str = "CHANGE_ME"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 720
    UPLOAD_DIR: str = "./uploads"

    AWS_REGION: str = "ap-southeast-1"
    AWS_ACCESS_KEY_ID: str | None = None
    AWS_SECRET_ACCESS_KEY: str | None = None
    S3_BUCKET: str = "CHANGE_ME"
    S3_PREFIX: str = "uploads"
    S3_PRESIGN_EXPIRE_SECONDS: int = 3600


    SEED_OWNER_USERNAME: str = "owner"
    SEED_OWNER_PASSWORD: str = "owner1234"
    SEED_OWNER_ROLE: str = "owner"

settings = Settings()
