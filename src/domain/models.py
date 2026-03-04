from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class ConversionStatus(Enum):
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class AudioFile:
    source_path: Path
    output_path: Path

    @property
    def filename(self) -> str:
        return self.source_path.name

    @property
    def stem(self) -> str:
        return self.source_path.stem


@dataclass
class ConversionResult:
    source_path: Path
    output_path: Path
    status: ConversionStatus
    error_message: str = ""
    duration_seconds: float = 0.0

    @property
    def is_success(self) -> bool:
        return self.status == ConversionStatus.SUCCESS

    @property
    def is_failed(self) -> bool:
        return self.status == ConversionStatus.FAILED


@dataclass
class BatchResult:
    results: list[ConversionResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.results)

    @property
    def succeeded(self) -> int:
        return sum(1 for r in self.results if r.is_success)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.is_failed)

    @property
    def skipped(self) -> int:
        return sum(1 for r in self.results if r.status == ConversionStatus.SKIPPED)

    @property
    def has_failures(self) -> bool:
        return self.failed > 0
