import re
from pathlib import Path


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def build_output_path(source: Path, output_dir: Path) -> Path:
    new_stem = re.sub(r'\s+', '_', source.stem)
    return output_dir / f"{new_stem}.wav"


def file_exists(path: Path) -> bool:
    return path.is_file()


def validate_source_file(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(f"Source file not found: {path}")
    if not path.is_file():
        raise ValueError(f"Path is not a file: {path}")
    if path.suffix.lower() != ".mp3":
        raise ValueError(f"File is not an MP3: {path}")
