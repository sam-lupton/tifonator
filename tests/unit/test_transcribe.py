"""Unit tests for tifonator.transcribe."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

import pytest

from tifonator.transcribe import transcribe_all, transcribe_file


@pytest.fixture()
def audio_file(tmp_path: Path) -> Path:
    f = tmp_path / "raw" / "abc123.mp3"
    f.parent.mkdir(parents=True)
    f.write_bytes(b"fake-audio")
    return f


@pytest.fixture()
def transcript_path(tmp_path: Path) -> Path:
    return tmp_path / "transcripts" / "abc123.txt"


def test_given_no_existing_transcript_when_transcribed_then_file_is_created(
    audio_file: Path, transcript_path: Path
) -> None:
    with patch("tifonator.transcribe.mlx_whisper") as mock_mlx:
        mock_mlx.transcribe.return_value = {"text": "  The false nine explained.  "}
        transcribe_file(audio_file, transcript_path)

    assert transcript_path.exists()
    assert transcript_path.read_text() == "The false nine explained."


def test_given_existing_transcript_when_transcribed_then_mlx_not_called(
    audio_file: Path, transcript_path: Path
) -> None:
    transcript_path.parent.mkdir(parents=True)
    transcript_path.write_text("existing content")

    with patch("tifonator.transcribe.mlx_whisper") as mock_mlx:
        transcribe_file(audio_file, transcript_path)
        mock_mlx.transcribe.assert_not_called()


def test_given_multiple_audio_files_when_transcribe_all_then_returns_all_paths(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    for name in ("ep1.mp3", "ep2.mp3", "ep3.mp3"):
        (raw_dir / name).write_bytes(b"fake")

    with patch("tifonator.transcribe.mlx_whisper") as mock_mlx:
        mock_mlx.transcribe.return_value = {"text": "transcript"}
        paths = transcribe_all(tmp_path)

    assert len(paths) == 3
    assert all(p.suffix == ".txt" for p in paths)
    assert mock_mlx.transcribe.call_count == 3


def test_given_limit_when_transcribe_all_then_only_processes_that_many(
    tmp_path: Path,
) -> None:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir(parents=True)
    for name in ("ep1.mp3", "ep2.mp3", "ep3.mp3"):
        (raw_dir / name).write_bytes(b"fake")

    with patch("tifonator.transcribe.mlx_whisper") as mock_mlx:
        mock_mlx.transcribe.return_value = {"text": "transcript"}
        paths = transcribe_all(tmp_path, limit=2)

    assert len(paths) == 2
    assert mock_mlx.transcribe.call_count == 2


def test_given_empty_raw_dir_when_transcribe_all_then_returns_empty_list(
    tmp_path: Path,
) -> None:
    (tmp_path / "raw").mkdir(parents=True)
    paths = transcribe_all(tmp_path)
    assert paths == []
