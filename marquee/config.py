from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_title: str = "Marquee"
    host: str = "0.0.0.0"
    port: int = 8080
    reload: bool = False
    refresh_interval_seconds: int = 60
    base_currency: str = "USD"


settings = Settings()
