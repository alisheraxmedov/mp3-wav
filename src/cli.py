from pathlib import Path
from typing import Annotated, Optional

import typer

from config import load_settings
from infrastructure.ffmpeg_adapter import FFmpegAdapter
from infrastructure.logging import setup_logging, get_logger
from services.converter_service import convert_batch
from services.discovery_service import discover_files, validate_file_paths

app = typer.Typer(
    name="antigravity-audio",
    help="Production-ready CLI tool for converting MP3 files to high-quality WAV using FFmpeg.",
    add_completion=False,
    no_args_is_help=True,
)


@app.command()
def convert(
    files: Annotated[
        Optional[list[Path]],
        typer.Option(
            "--files",
            help="Explicit list of MP3 file paths to convert.",
            exists=False,
        ),
    ] = None,
    input_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--input-dir",
            help="Directory to scan for MP3 files.",
        ),
    ] = None,
    output_dir: Annotated[
        Optional[Path],
        typer.Option(
            "--output-dir",
            help="Directory where WAV files will be written.",
        ),
    ] = None,
    workers: Annotated[
        Optional[int],
        typer.Option(
            "--workers",
            help="Number of concurrent conversion workers.",
            min=1,
        ),
    ] = None,
    overwrite: Annotated[
        Optional[bool],
        typer.Option(
            "--overwrite/--no-overwrite",
            help="Overwrite existing WAV files.",
        ),
    ] = None,
    pattern: Annotated[
        str,
        typer.Option(
            "--pattern",
            help="Glob pattern for file discovery.",
        ),
    ] = "*.mp3",
    recursive: Annotated[
        bool,
        typer.Option(
            "--recursive/--no-recursive",
            help="Search subdirectories recursively.",
        ),
    ] = True,
) -> None:
    """Convert MP3 files to high-quality PCM WAV format."""
    settings = load_settings()
    setup_logging(settings.log_level)
    logger = get_logger("cli")

    resolved_output = output_dir or settings.output_dir
    resolved_workers = workers if workers is not None else settings.workers
    resolved_overwrite = overwrite if overwrite is not None else settings.overwrite

    if not FFmpegAdapter.is_available():
        typer.echo(
            "Error: FFmpeg is not installed or not found in PATH.", err=True)
        raise typer.Exit(code=1)

    if files:
        logger.info(
            "Mode: explicit file list (%d file(s) provided)", len(files))
        discovered = validate_file_paths(files)
    elif input_dir:
        logger.info("Mode: directory scan '%s'", input_dir)
        try:
            discovered = discover_files(
                input_dir, pattern=pattern, recursive=recursive)
        except (FileNotFoundError, NotADirectoryError) as exc:
            typer.echo(f"Error: {exc}", err=True)
            raise typer.Exit(code=1)
    else:
        typer.echo(
            "Error: Provide either --files or --input-dir.\n"
            "Run 'antigravity-audio convert --help' for usage.",
            err=True,
        )
        raise typer.Exit(code=1)

    if not discovered:
        typer.echo("No MP3 files found to convert.", err=True)
        raise typer.Exit(code=0)

    typer.echo(f"Converting {len(discovered)} file(s) → {resolved_output}")

    batch_result = convert_batch(
        files=discovered,
        output_dir=resolved_output,
        workers=resolved_workers,
        overwrite=resolved_overwrite,
    )

    typer.echo(
        f"\nDone: {batch_result.succeeded} succeeded, "
        f"{batch_result.failed} failed, "
        f"{batch_result.skipped} skipped."
    )

    if batch_result.has_failures:
        raise typer.Exit(code=1)


@app.command()
def info() -> None:
    """Show tool information and FFmpeg availability."""
    from __init__ import __version__

    typer.echo(f"antigravity-audio v{__version__}")
    typer.echo(f"FFmpeg available: {FFmpegAdapter.is_available()}")


if __name__ == "__main__":
    app()
