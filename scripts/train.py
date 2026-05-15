"""CLI: prepare dataset and run LoRA fine-tuning."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

DATA_DIR = Path(__file__).parent.parent / "data"
MODELS_DIR = Path(__file__).parent.parent / "models"

app = typer.Typer()


@app.command()
def main(
    base_model: Annotated[
        str, typer.Option(help="HuggingFace base model ID")
    ] = "microsoft/Phi-3-mini-4k-instruct",
    data_dir: Annotated[Path, typer.Option(help="Root data directory")] = DATA_DIR,
    output_dir: Annotated[Path, typer.Option(help="Where to save fine-tuned weights")] = MODELS_DIR,
    epochs: Annotated[int, typer.Option(help="Training epochs")] = 3,
) -> None:
    """Fine-tune a base LLM on Tifo transcript data using LoRA."""
    from tifonator.train import train

    train(data_dir=data_dir, output_dir=output_dir, base_model=base_model, epochs=epochs)


if __name__ == "__main__":
    app()
