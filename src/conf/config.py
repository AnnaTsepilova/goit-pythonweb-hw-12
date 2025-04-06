from pydantic import ConfigDict, EmailStr
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str = "postgresql+asyncpg://user:password@host:5432/database"

    REDIS_HOST: str = ""
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str = None

    JWT_SECRET: str = "jwt_secret"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_SECONDS: int = 3600
    REFRESH_TOKEN_EXPIRATION_MINUTES: int = 60 * 24 * 7

    MAIL_USERNAME: EmailStr = "example@meta.ua"
    MAIL_PASSWORD: str = "secretPassword"
    MAIL_FROM: EmailStr = "example@meta.ua"
    MAIL_PORT: int = 465
    MAIL_SERVER: str = "smtp.meta.ua"
    MAIL_FROM_NAME: str = "Rest API Service"
    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True
    USE_CREDENTIALS: bool = True
    VALIDATE_CERTS: bool = True

    CLOUDINARY_NAME: str = "ACCOUNT_NAME"
    CLOUDINARY_API_KEY: str = "API_KEY"
    CLOUDINARY_API_SECRET: str = "API_SECRET"

    model_config = ConfigDict(
        extra="ignore", env_file=".env", env_file_encoding="utf-8", case_sensitive=True
    )

settings = Settings()
