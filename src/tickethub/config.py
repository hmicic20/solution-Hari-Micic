from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "TicketHub"
    app_env: str = "dev"
    database_url: str = "sqlite+aiosqlite:///./tickethub.db"
    sync_on_startup: bool = False

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()
