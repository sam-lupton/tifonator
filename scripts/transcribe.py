"""CLI: transcribe all files in data/raw/ and write to data/transcripts/."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

DATA_DIR = Path(__file__).parent.parent / "data"

app = typer.Typer()


@app.command()
def main(
    model: Annotated[str, typer.Option(help="Whisper model size")] = "medium",
    limit: Annotated[int, typer.Option(help="Max episodes to transcribe")] = 0,
    data_dir: Annotated[Path, typer.Option(help="Root data directory")] = DATA_DIR,
) -> None:
    """Transcribe downloaded episodes with Whisper."""
    from tifonator.transcribe import transcribe_all

    transcribe_all(data_dir, model_name=model, limit=limit or None)


if __name__ == "__main__":
    app()
