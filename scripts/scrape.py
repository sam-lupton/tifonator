"""CLI: scrape all episodes and download audio to data/raw/."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from tifonator.scrape import download_all, fetch_feed

DATA_DIR = Path(__file__).parent.parent / "data"

app = typer.Typer()


@app.command()
def main(
    limit: Annotated[int | None, typer.Option(help="Max episodes to download")] = None,
    delay: Annotated[float, typer.Option(help="Seconds between downloads")] = 1.0,
    data_dir: Annotated[Path, typer.Option(help="Root data directory")] = DATA_DIR,
) -> None:
    """Download Tifo podcast episodes from the RSS feed."""
    typer.echo("Fetching feed…")
    feed = fetch_feed()
    typer.echo(f"Found {len(feed.episodes)} episodes in feed.")

    paths = download_all(feed, data_dir, limit=limit, delay=delay)
    typer.echo(f"\nDone. {len(paths)} files in {data_dir / 'raw'}")


if __name__ == "__main__":
    app()
