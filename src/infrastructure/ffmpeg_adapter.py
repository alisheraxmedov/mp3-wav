import subprocess
import time
from pathlib import Path

from infrastructure.logging import get_logger

logger = get_logger("ffmpeg")


class ConversionError(Exception):
    pass


class FFmpegAdapter:
    FFMPEG_BINARY = "ffmpeg"

    def convert_to_wav(self, source: Path, destination: Path, overwrite: bool = False) -> float:
        command = self._build_command(source, destination, overwrite)
        logger.debug("Running command: %s", " ".join(command))

        start_time = time.monotonic()

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=False,
            )
        except FileNotFoundError:
            raise ConversionError(
                f"FFmpeg binary not found. Ensure '{self.FFMPEG_BINARY}' is installed and in PATH."
            )

        elapsed = time.monotonic() - start_time

        if result.returncode != 0:
            raise ConversionError(
                f"FFmpeg failed for '{source.name}' (exit code {result.returncode}): "
                f"{result.stderr.strip()}"
            )

        return elapsed

    def _build_command(self, source: Path, destination: Path, overwrite: bool) -> list[str]:
        command = [
            self.FFMPEG_BINARY,
            "-i", str(source),
            "-c:a", "pcm_s16le",
            "-map_metadata", "0",
        ]

        if overwrite:
            command.append("-y")
        else:
            command.append("-n")

        command.append(str(destination))
        return command

    @staticmethod
    def is_available() -> bool:
        try:
            result = subprocess.run(
                ["ffmpeg", "-version"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
