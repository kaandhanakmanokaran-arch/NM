from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "FitBuddy"
    app_env: str = "development"
    database_url: str = "sqlite:///./fitbuddy.db"
    google_api_key: str | None = None
    workout_model: str = "gemini-1.5-pro"
    nutrition_model: str = "gemini-1.5-flash"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
