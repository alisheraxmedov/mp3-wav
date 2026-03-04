# Antigravity Audio

Production-ready CLI tool for converting MP3 files to high-quality WAV using FFmpeg.

Supports batch processing, concurrent workers, recursive directory scanning, and is fully containerized with Docker.

## Features

- Convert MP3 → WAV (PCM 16-bit, lossless container)
- Batch conversion with configurable concurrency
- Recursive directory scanning with glob patterns
- Explicit file list or directory-based input
- Skip or overwrite existing outputs
- Environment-based configuration with `.env` support
- Docker-ready with non-root user
- Clean architecture with separated concerns

## Requirements

- **Python 3.11+**
- **FFmpeg** installed and available in `PATH`
- **uv** for dependency management

## Installation

### 1. Install FFmpeg
To use this CLI tool locally, you **must have FFmpeg installed** on your system.

**macOS:**
```bash
brew install ffmpeg
```

**Linux (Debian/Ubuntu):**
```bash
sudo apt update
sudo apt install ffmpeg
```

**Windows:**
The easiest way is using `winget` or `chocolatey`:
```bash
winget install gyan.ffmpeg
# OR
choco install ffmpeg
```
*(Ensure FFmpeg is added to your system PATH)*

### 2. Local Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone and install
cd mp3-wav
uv sync

# Verify
uv run antigravity-audio --help
```

### Docker

```bash
docker build -t antigravity-audio .
docker run --rm antigravity-audio --help
```

## Configuration

All settings can be configured via environment variables or a `.env` file.

| Variable                | Default     | Description                         |
|-------------------------|-------------|-------------------------------------|
| `ANTIGRAVITY_INPUT_DIR` | `./audios/mp3`| Default input directory             |
| `ANTIGRAVITY_OUTPUT_DIR`| `./audios/wav`| Default output directory            |
| `ANTIGRAVITY_WORKERS`   | `CPU / 2`   | Number of concurrent workers        |
| `ANTIGRAVITY_LOG_LEVEL` | `INFO`      | Logging level (DEBUG, INFO, etc.)   |
| `ANTIGRAVITY_OVERWRITE` | `false`     | Overwrite existing WAV files        |

Copy `.env.example` to `.env` and edit as needed:

```bash
cp .env.example .env
```

## Usage

### Convert Explicit Files

```bash
uv run antigravity-audio convert \
  --files /path/to/song1.mp3 /path/to/song2.mp3 \
  --output-dir ./output
```

### Convert All MP3s in a Directory

```bash
uv run antigravity-audio convert \
  --input-dir ./music \
  --output-dir ./wav-output
```

### With Options

```bash
uv run antigravity-audio convert \
  --input-dir ./music \
  --output-dir ./output \
  --workers 8 \
  --overwrite \
  --recursive \
  --pattern "*.mp3"
```

### Non-Recursive Scan

```bash
uv run antigravity-audio convert \
  --input-dir ./music \
  --output-dir ./output \
  --no-recursive
```

### Check Tool Info

```bash
uv run antigravity-audio info
```

### Docker Usage

```bash
# Convert files using volume mounts
docker run --rm \
  -v /host/music:/app/input \
  -v /host/output:/app/output \
  antigravity-audio convert \
  --input-dir /app/input \
  --output-dir /app/output

# With Docker Compose
docker compose up
```

## Audio Quality Notes

> **Important:** MP3 is a lossy format. Converting MP3 → WAV produces a lossless
> container (PCM 16-bit), but **cannot restore audio information lost during the
> original MP3 encoding**. The conversion preserves the existing quality without
> any additional lossy compression or resampling.

The tool uses FFmpeg with: `ffmpeg -i input.mp3 -c:a pcm_s16le -map_metadata 0 output.wav`

## Development

### Setup

```bash
uv sync
```

### Run Tests

```bash
uv run pytest tests/ -v
```

### Lint

```bash
uv run ruff check src/ tests/
```

### Format

```bash
uv run ruff format src/ tests/
```

## Project Structure

```
mp3-wav/
├── pyproject.toml
├── README.md
├── .env.example
├── Dockerfile
├── docker-compose.yml
├── src/
│   ├── __init__.py
│   ├── cli.py                    # Typer CLI entrypoint
│   ├── config.py                 # pydantic-settings configuration
│   ├── domain/
│   │   └── models.py             # AudioFile, ConversionResult, BatchResult
│   ├── services/
│   │   ├── converter_service.py  # Batch conversion orchestration
│   │   └── discovery_service.py  # File discovery and validation
│   └── infrastructure/
│       ├── ffmpeg_adapter.py     # FFmpeg subprocess wrapper
│       ├── filesystem.py         # Path and directory utilities
│       └── logging.py            # Logging configuration
└── tests/
    ├── test_converter_service.py
    ├── test_discovery_service.py
    ├── test_ffmpeg_adapter.py
    └── test_filesystem.py
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `FFmpeg binary not found` | Install FFmpeg: `brew install ffmpeg` (macOS) or `apt install ffmpeg` (Linux) |
| `Permission denied` on output directory | Ensure write permissions on the output path |
| `No MP3 files found` | Check `--input-dir` path and `--pattern` value |
| Slow conversion | Increase `--workers` (default is half CPU count) |

## License

MIT
