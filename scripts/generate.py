"""CLI: generate a new episode given a topic."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

MODELS_DIR = Path(__file__).parent.parent / "models"

app = typer.Typer()


@app.command()
def main(
    topic: Annotated[str, typer.Argument(help="Topic for the generated episode")],
    model_dir: Annotated[Path, typer.Option(help="Path to fine-tuned model weights")] = MODELS_DIR,
    voice_sample: Annotated[Path, typer.Option(help="Short audio clip for voice cloning")] = Path(
        "voices/host.wav"
    ),
    output: Annotated[Path, typer.Option(help="Output .wav path")] = Path("output.wav"),
) -> None:
    """Generate a Tifo-style podcast episode on the given topic."""
    from tifonator.generate import generate_episode

    generate_episode(topic=topic, model_dir=model_dir, voice_sample=voice_sample, output=output)


if __name__ == "__main__":
    app()
