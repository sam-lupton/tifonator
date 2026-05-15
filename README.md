# Tifonator

AI-generated podcast episodes in the style of the [Tifo Football Podcast](https://tifofootball.com/tifo-podcast/).

## How it works

Three phases, run once each:

| Phase | What it does |
|-------|-------------|
| **1. Scrape** | Downloads all episodes from the RSS feed |
| **2. Train** | Transcribes audio with Whisper, fine-tunes an LLM on the transcripts |
| **3. Generate** | Generates a new script, synthesises speech in the hosts' voices via Coqui XTTS |

## Quick start (non-technical)

> Requires [Docker](https://docs.docker.com/get-docker/) — nothing else.

```bash
docker compose up
```

Then open http://localhost:7860 in your browser.

## Developer setup

```bash
uv sync
uv run tifonator
```

### Run each phase manually

```bash
# Phase 1 — scrape episodes
uv run python scripts/scrape.py

# Phase 2 — transcribe + fine-tune
uv run python scripts/transcribe.py
uv run python scripts/train.py

# Phase 3 — generate an episode
uv run python scripts/generate.py --topic "The false nine position"
```

## Project layout

```
tifonator/        # Core library
  scrape.py       # RSS feed + audio downloader
  transcribe.py   # Whisper wrapper
  train.py        # LoRA fine-tuning on transcripts
  generate.py     # LLM script generation + XTTS voice synthesis
  app.py          # Gradio UI
scripts/          # CLI entry points for each phase
data/
  raw/            # Downloaded .mp3 files (gitignored)
  transcripts/    # Whisper .txt output (gitignored)
  dataset/        # Prepared training data (gitignored)
models/           # Fine-tuned weights (gitignored)
tests/
  contracts/      # Data boundary tests
```
