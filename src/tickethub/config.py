from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TicketHub"
    app_env: str = "dev"
    database_url: str = "sqlite+aiosqlite:///./tickethub.db"
    sync_on_startup: bool = False
    redis_url: str = "redis://localhost:6379/0"
    log_level: str = "INFO"
    cache_enabled: bool = False
    cache_ttl_seconds: int = 60
    rate_limit_default: str = "100/minute"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
