from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from infrastructure.ffmpeg_adapter import ConversionError, FFmpegAdapter


class TestBuildCommand:
    def setup_method(self) -> None:
        self.adapter = FFmpegAdapter()

    def test_basic_command_structure(self) -> None:
        cmd = self.adapter._build_command(
            Path("/in/a.mp3"), Path("/out/a.wav"), overwrite=False)
        assert cmd[0] == "ffmpeg"
        assert "-i" in cmd
        assert str(Path("/in/a.mp3")) in cmd
        assert "-c:a" in cmd
        assert "pcm_s16le" in cmd
        assert str(Path("/out/a.wav")) in cmd

    def test_overwrite_flag_adds_dash_y(self) -> None:
        cmd = self.adapter._build_command(
            Path("/in/a.mp3"), Path("/out/a.wav"), overwrite=True)
        assert "-y" in cmd
        assert "-n" not in cmd

    def test_no_overwrite_flag_adds_dash_n(self) -> None:
        cmd = self.adapter._build_command(
            Path("/in/a.mp3"), Path("/out/a.wav"), overwrite=False)
        assert "-n" in cmd
        assert "-y" not in cmd

    def test_preserves_metadata(self) -> None:
        cmd = self.adapter._build_command(
            Path("/in/a.mp3"), Path("/out/a.wav"), overwrite=False)
        assert "-map_metadata" in cmd
        idx = cmd.index("-map_metadata")
        assert cmd[idx + 1] == "0"


class TestConvertToWav:
    def setup_method(self) -> None:
        self.adapter = FFmpegAdapter()

    @patch("infrastructure.ffmpeg_adapter.subprocess.run")
    def test_successful_conversion_returns_elapsed_time(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        elapsed = self.adapter.convert_to_wav(
            Path("/in/a.mp3"), Path("/out/a.wav"))
        assert elapsed >= 0
        mock_run.assert_called_once()

    @patch("infrastructure.ffmpeg_adapter.subprocess.run")
    def test_failed_conversion_raises_error(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(
            returncode=1, stderr="codec not found")
        with pytest.raises(ConversionError, match="FFmpeg failed"):
            self.adapter.convert_to_wav(Path("/in/a.mp3"), Path("/out/a.wav"))

    @patch("infrastructure.ffmpeg_adapter.subprocess.run")
    def test_missing_ffmpeg_raises_error(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(ConversionError, match="FFmpeg binary not found"):
            self.adapter.convert_to_wav(Path("/in/a.mp3"), Path("/out/a.wav"))


class TestIsAvailable:
    @patch("infrastructure.ffmpeg_adapter.subprocess.run")
    def test_returns_true_when_ffmpeg_exists(self, mock_run: MagicMock) -> None:
        mock_run.return_value = MagicMock(returncode=0)
        assert FFmpegAdapter.is_available() is True

    @patch("infrastructure.ffmpeg_adapter.subprocess.run")
    def test_returns_false_when_ffmpeg_missing(self, mock_run: MagicMock) -> None:
        mock_run.side_effect = FileNotFoundError()
        assert FFmpegAdapter.is_available() is False
