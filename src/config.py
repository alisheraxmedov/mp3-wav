import os
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix="MP3WAV_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    input_dir: Path = Path("./audios/mp3")
    output_dir: Path = Path("./audios/wav")
    workers: int = max(1, (os.cpu_count() or 4) // 2)
    log_level: str = "INFO"
    overwrite: bool = False


def load_settings() -> Settings:
    return Settings()
