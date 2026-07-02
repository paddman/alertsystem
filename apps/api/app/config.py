from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "eGov Workflow Platform"
    app_env: str = "development"
    database_url: str = "sqlite:///./egov.db"
    redis_url: str = "redis://localhost:6379/0"
    audit_hmac_key: str = "change-me-before-production"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
