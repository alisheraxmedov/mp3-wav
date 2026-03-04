from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from domain.models import (
    AudioFile,
    BatchResult,
    ConversionResult,
    ConversionStatus,
)
from infrastructure.ffmpeg_adapter import ConversionError, FFmpegAdapter
from infrastructure.filesystem import (
    build_output_path,
    ensure_directory,
    file_exists,
)
from infrastructure.logging import get_logger

logger = get_logger("converter")


def _convert_single_file(
    source: Path,
    destination: Path,
    overwrite: bool,
) -> ConversionResult:
    if file_exists(destination) and not overwrite:
        return ConversionResult(
            source_path=source,
            output_path=destination,
            status=ConversionStatus.SKIPPED,
            error_message="Output file already exists",
        )

    adapter = FFmpegAdapter()
    try:
        elapsed = adapter.convert_to_wav(
            source, destination, overwrite=overwrite)
        return ConversionResult(
            source_path=source,
            output_path=destination,
            status=ConversionStatus.SUCCESS,
            duration_seconds=elapsed,
        )
    except ConversionError as exc:
        return ConversionResult(
            source_path=source,
            output_path=destination,
            status=ConversionStatus.FAILED,
            error_message=str(exc),
        )


def convert_batch(
    files: list[Path],
    output_dir: Path,
    workers: int = 4,
    overwrite: bool = False,
) -> BatchResult:
    ensure_directory(output_dir)

    audio_files = [
        AudioFile(source_path=f, output_path=build_output_path(f, output_dir))
        for f in files
    ]

    logger.info("Starting batch conversion: %d file(s), %d worker(s)",
                len(audio_files), workers)

    batch_result = BatchResult()

    with ProcessPoolExecutor(max_workers=workers) as executor:
        future_to_file = {
            executor.submit(
                _convert_single_file,
                af.source_path,
                af.output_path,
                overwrite,
            ): af
            for af in audio_files
        }

        for future in as_completed(future_to_file):
            audio_file = future_to_file[future]
            try:
                result = future.result()
            except Exception as exc:
                result = ConversionResult(
                    source_path=audio_file.source_path,
                    output_path=audio_file.output_path,
                    status=ConversionStatus.FAILED,
                    error_message=str(exc),
                )

            batch_result.results.append(result)

            if result.is_success:
                logger.info(
                    "✓ Converted '%s' (%.2fs)",
                    audio_file.filename,
                    result.duration_seconds,
                )
            elif result.status == ConversionStatus.SKIPPED:
                logger.info("⊘ Skipped '%s': %s",
                            audio_file.filename, result.error_message)
            else:
                logger.error("✗ Failed '%s': %s",
                             audio_file.filename, result.error_message)

    logger.info(
        "Batch complete: %d succeeded, %d failed, %d skipped (of %d total)",
        batch_result.succeeded,
        batch_result.failed,
        batch_result.skipped,
        batch_result.total,
    )

    return batch_result
