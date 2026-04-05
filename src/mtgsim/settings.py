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

    # OCR pipeline
    ocr_preprocess_grayscale: bool = True
    ocr_preprocess_contrast: float = 1.5
    ocr_preprocess_sharpness: float = 2.0
    ocr_preprocess_scale: float = 2.0
    ocr_preprocess_binarize_threshold: int = 0
    ocr_preprocess_denoise_kernel: int = 0
    ocr_psm: int = 6
    ocr_lang: str = "eng"
    ocr_match_threshold: float = 60.0
    ocr_match_name_weight: float = 3.0
    ocr_match_type_line_weight: float = 1.0
    ocr_match_oracle_text_weight: float = 2.0
    ocr_match_name_scorer: str = "partial_ratio"
    ocr_match_text_scorer: str = "token_set_ratio"

    # App paths
    mtgsim_app_dir: str = ""


settings = Settings()
