FROM python:3.11-slim AS base

RUN apt-get update && \
    apt-get install -y --no-install-recommends ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN groupadd --gid 1000 appuser && \
    useradd --uid 1000 --gid 1000 --create-home appuser

WORKDIR /app

COPY pyproject.toml README.md uv.lock* ./

RUN uv sync --no-dev --no-install-project

COPY src/ ./src/

RUN mkdir -p /app/audios/mp3 /app/audios/wav && \
    chown -R appuser:appuser /app

ENV PYTHONPATH=/app/src
ENV PATH="/app/.venv/bin:$PATH"

USER appuser

ENTRYPOINT ["python", "src/cli.py"]
CMD ["--help"]
