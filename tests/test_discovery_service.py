from pathlib import Path

import pytest

from services.discovery_service import discover_files, validate_file_paths


@pytest.fixture
def sample_dir(tmp_path: Path) -> Path:
    (tmp_path / "song1.mp3").touch()
    (tmp_path / "song2.mp3").touch()
    (tmp_path / "readme.txt").touch()
    sub = tmp_path / "subdir"
    sub.mkdir()
    (sub / "song3.mp3").touch()
    (sub / "image.png").touch()
    return tmp_path


class TestDiscoverFiles:
    def test_discovers_all_mp3_recursively(self, sample_dir: Path) -> None:
        result = discover_files(sample_dir, recursive=True)
        assert len(result) == 3
        names = {f.name for f in result}
        assert names == {"song1.mp3", "song2.mp3", "song3.mp3"}

    def test_discovers_mp3_non_recursively(self, sample_dir: Path) -> None:
        result = discover_files(sample_dir, recursive=False)
        assert len(result) == 2
        names = {f.name for f in result}
        assert names == {"song1.mp3", "song2.mp3"}

    def test_custom_pattern(self, sample_dir: Path) -> None:
        result = discover_files(sample_dir, pattern="*.txt", recursive=False)
        assert len(result) == 1
        assert result[0].name == "readme.txt"

    def test_raises_on_missing_directory(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            discover_files(tmp_path / "nonexistent")

    def test_raises_on_file_instead_of_directory(self, sample_dir: Path) -> None:
        with pytest.raises(NotADirectoryError):
            discover_files(sample_dir / "song1.mp3")

    def test_empty_directory(self, tmp_path: Path) -> None:
        empty = tmp_path / "empty"
        empty.mkdir()
        result = discover_files(empty)
        assert result == []


class TestValidateFilePaths:
    def test_validates_existing_mp3_files(self, sample_dir: Path) -> None:
        paths = [sample_dir / "song1.mp3", sample_dir / "song2.mp3"]
        result = validate_file_paths(paths)
        assert len(result) == 2

    def test_skips_nonexistent_files(self, sample_dir: Path) -> None:
        paths = [sample_dir / "song1.mp3", sample_dir / "missing.mp3"]
        result = validate_file_paths(paths)
        assert len(result) == 1

    def test_skips_non_mp3_files(self, sample_dir: Path) -> None:
        paths = [sample_dir / "song1.mp3", sample_dir / "readme.txt"]
        result = validate_file_paths(paths)
        assert len(result) == 1
        assert result[0].name == "song1.mp3"

    def test_skips_directories(self, sample_dir: Path) -> None:
        paths = [sample_dir / "subdir"]
        result = validate_file_paths(paths)
        assert result == []

    def test_empty_input(self) -> None:
        result = validate_file_paths([])
        assert result == []
