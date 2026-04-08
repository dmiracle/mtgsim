"""Application settings loaded from environment variables and .env file."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # API server
    debug: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8001

    # OpenAI
    openai_api_key: str = ""

    # Scan endpoint
    scan_rate_limit: int = 10
    scan_rate_window: int = 60
    scan_default_pipeline: str = "openai"
    scan_fuzzy_threshold: int = 92

    # App paths
    mtgsim_app_dir: str = ""


settings = Settings()
