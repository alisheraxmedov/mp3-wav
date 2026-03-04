from pathlib import Path

import pytest

from infrastructure.filesystem import (
    build_output_path,
    ensure_directory,
    file_exists,
    validate_source_file,
)


class TestBuildOutputPath:
    def test_converts_mp3_extension_to_wav(self) -> None:
        source = Path("/data/music/track.mp3")
        output_dir = Path("/output")
        result = build_output_path(source, output_dir)
        assert result == Path("/output/track.wav")

    def test_handles_nested_source_path(self) -> None:
        source = Path("/a/b/c/deep_track.mp3")
        output_dir = Path("/flat_output")
        result = build_output_path(source, output_dir)
        assert result == Path("/flat_output/deep_track.wav")

    def test_handles_spaces_in_filename(self) -> None:
        source = Path("/data/my song.mp3")
        output_dir = Path("/output")
        result = build_output_path(source, output_dir)
        assert result == Path("/output/my song.wav")


class TestEnsureDirectory:
    def test_creates_new_directory(self, tmp_path: Path) -> None:
        new_dir = tmp_path / "new" / "nested"
        result = ensure_directory(new_dir)
        assert result.is_dir()

    def test_existing_directory_is_noop(self, tmp_path: Path) -> None:
        result = ensure_directory(tmp_path)
        assert result == tmp_path


class TestFileExists:
    def test_returns_true_for_existing_file(self, tmp_path: Path) -> None:
        f = tmp_path / "test.wav"
        f.touch()
        assert file_exists(f) is True

    def test_returns_false_for_missing_file(self, tmp_path: Path) -> None:
        assert file_exists(tmp_path / "nope.wav") is False

    def test_returns_false_for_directory(self, tmp_path: Path) -> None:
        assert file_exists(tmp_path) is False


class TestValidateSourceFile:
    def test_valid_mp3_passes(self, tmp_path: Path) -> None:
        f = tmp_path / "valid.mp3"
        f.touch()
        validate_source_file(f)

    def test_raises_on_missing_file(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            validate_source_file(tmp_path / "missing.mp3")

    def test_raises_on_directory(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="not a file"):
            validate_source_file(tmp_path)

    def test_raises_on_non_mp3(self, tmp_path: Path) -> None:
        f = tmp_path / "audio.flac"
        f.touch()
        with pytest.raises(ValueError, match="not an MP3"):
            validate_source_file(f)
