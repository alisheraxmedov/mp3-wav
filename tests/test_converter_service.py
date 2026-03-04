from pathlib import Path
from unittest.mock import MagicMock, patch

from domain.models import ConversionStatus
from services.converter_service import _convert_single_file, convert_batch


class TestConvertSingleFile:
    @patch("services.converter_service.FFmpegAdapter")
    def test_successful_conversion(self, mock_adapter_class: MagicMock, tmp_path: Path) -> None:
        source = tmp_path / "test.mp3"
        source.touch()
        dest = tmp_path / "test.wav"

        mock_adapter = mock_adapter_class.return_value
        mock_adapter.convert_to_wav.return_value = 1.5

        result = _convert_single_file(source, dest, overwrite=False)

        assert result.status == ConversionStatus.SUCCESS
        assert result.duration_seconds == 1.5

    def test_skips_existing_file_without_overwrite(self, tmp_path: Path) -> None:
        source = tmp_path / "test.mp3"
        source.touch()
        dest = tmp_path / "test.wav"
        dest.touch()

        result = _convert_single_file(source, dest, overwrite=False)

        assert result.status == ConversionStatus.SKIPPED

    @patch("services.converter_service.FFmpegAdapter")
    def test_overwrites_existing_file_when_flag_set(
        self, mock_adapter_class: MagicMock, tmp_path: Path
    ) -> None:
        source = tmp_path / "test.mp3"
        source.touch()
        dest = tmp_path / "test.wav"
        dest.touch()

        mock_adapter = mock_adapter_class.return_value
        mock_adapter.convert_to_wav.return_value = 0.8

        result = _convert_single_file(source, dest, overwrite=True)

        assert result.status == ConversionStatus.SUCCESS

    @patch("services.converter_service.FFmpegAdapter")
    def test_handles_conversion_error(
        self, mock_adapter_class: MagicMock, tmp_path: Path
    ) -> None:
        from infrastructure.ffmpeg_adapter import ConversionError

        source = tmp_path / "test.mp3"
        source.touch()
        dest = tmp_path / "test.wav"

        mock_adapter = mock_adapter_class.return_value
        mock_adapter.convert_to_wav.side_effect = ConversionError(
            "ffmpeg crashed")

        result = _convert_single_file(source, dest, overwrite=False)

        assert result.status == ConversionStatus.FAILED
        assert "ffmpeg crashed" in result.error_message


class TestConvertBatch:
    @patch("services.converter_service._convert_single_file")
    def test_batch_returns_correct_summary(
        self, mock_convert: MagicMock, tmp_path: Path
    ) -> None:
        from domain.models import ConversionResult

        files = [tmp_path / "a.mp3", tmp_path / "b.mp3"]
        for f in files:
            f.touch()

        mock_convert.side_effect = [
            ConversionResult(
                source_path=files[0],
                output_path=tmp_path / "a.wav",
                status=ConversionStatus.SUCCESS,
                duration_seconds=1.0,
            ),
            ConversionResult(
                source_path=files[1],
                output_path=tmp_path / "b.wav",
                status=ConversionStatus.FAILED,
                error_message="error",
            ),
        ]

        batch = convert_batch(files, tmp_path / "out",
                              workers=1, overwrite=False)

        assert batch.total == 2
        assert batch.succeeded == 1
        assert batch.failed == 1
        assert batch.has_failures is True
