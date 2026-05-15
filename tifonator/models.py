"""Domain models — the contract between every module in this project."""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, field_validator


class Episode(BaseModel):
    id: str
    title: str
    pub_date: datetime
    duration_seconds: int
    audio_url: str
    audio_bytes: int
    description: str
    episode_type: str = "full"

    @field_validator("duration_seconds", mode="before")
    @classmethod
    def parse_duration(cls, v: object) -> int:
        if isinstance(v, int):
            return v
        # Accept "HH:MM:SS" or "MM:SS"
        parts = str(v).split(":")
        seconds = 0
        for part in parts:
            seconds = seconds * 60 + int(part)
        return seconds

    def audio_path(self, data_dir: Path) -> Path:
        return data_dir / "raw" / f"{self.id}.mp3"

    def transcript_path(self, data_dir: Path) -> Path:
        return data_dir / "transcripts" / f"{self.id}.txt"


class FeedMeta(BaseModel):
    show_title: str
    show_description: str
    episodes: list[Episode]
