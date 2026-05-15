"""Phase 2a: transcribe downloaded audio files with mlx-whisper."""

from __future__ import annotations

from pathlib import Path

from tqdm import tqdm

try:
    import mlx_whisper
except ImportError:
    mlx_whisper = None  # type: ignore[assignment]

DEFAULT_MODEL = "mlx-community/whisper-large-v3-turbo"


def transcribe_file(
    audio_path: Path, transcript_path: Path, *, model_name: str = DEFAULT_MODEL
) -> Path:
    """Transcribe a single audio file. Skips if transcript already exists."""
    if transcript_path.exists() and transcript_path.stat().st_size > 0:
        return transcript_path

    if mlx_whisper is None:
        raise RuntimeError("mlx-whisper is not installed. Run: uv sync --extra train")

    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    result = mlx_whisper.transcribe(str(audio_path), path_or_hf_repo=model_name)
    transcript_path.write_text(result["text"].strip(), encoding="utf-8")
    return transcript_path


def transcribe_all(
    data_dir: Path,
    *,
    model_name: str = DEFAULT_MODEL,
    limit: int | None = None,
) -> list[Path]:
    """Transcribe all .mp3 files in data/raw/ that don't yet have a transcript."""
    raw_dir = data_dir / "raw"
    audio_files = sorted(raw_dir.glob("*.mp3"))
    if limit:
        audio_files = audio_files[:limit]

    paths: list[Path] = []
    for audio in tqdm(audio_files, desc="Transcribing", unit="ep"):
        transcript = data_dir / "transcripts" / f"{audio.stem}.txt"
        paths.append(transcribe_file(audio, transcript, model_name=model_name))

    return paths
