from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    DATABASE_URL: str = "postgresql+psycopg2://raybeam:raybeam@localhost:5432/raybeam"
    SECRET_KEY: str = "changeme"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    ENABLE_CORS: bool = False
    CORS_ORIGINS: list[str] = []

    ADMIN_USERNAME: str | None = None
    ADMIN_PASSWORD: str | None = None

    LICENSE_FILE: str = "/data/license.rbl"


settings = Settings()
