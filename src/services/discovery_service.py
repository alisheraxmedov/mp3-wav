from pathlib import Path

from infrastructure.logging import get_logger

logger = get_logger("discovery")

DEFAULT_PATTERN = "*.mp3"


def discover_files(
    input_dir: Path,
    pattern: str = DEFAULT_PATTERN,
    recursive: bool = True,
) -> list[Path]:
    if not input_dir.exists():
        raise FileNotFoundError(f"Input directory not found: {input_dir}")
    if not input_dir.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {input_dir}")

    if recursive:
        files = sorted(input_dir.rglob(pattern))
    else:
        files = sorted(input_dir.glob(pattern))

    logger.info("Discovered %d file(s) in '%s' (pattern='%s', recursive=%s)",
                len(files), input_dir, pattern, recursive)
    return files


def validate_file_paths(file_paths: list[Path]) -> list[Path]:
    validated: list[Path] = []
    for path in file_paths:
        resolved = Path(path).resolve()
        if not resolved.exists():
            logger.warning("File not found, skipping: %s", path)
            continue
        if not resolved.is_file():
            logger.warning("Not a file, skipping: %s", path)
            continue
        if resolved.suffix.lower() != ".mp3":
            logger.warning("Not an MP3 file, skipping: %s", path)
            continue
        validated.append(resolved)

    logger.info("Validated %d of %d provided file path(s)",
                len(validated), len(file_paths))
    return validated
