"""Phase 1: fetch episode metadata and download audio from the RSS feed."""

from __future__ import annotations

import re
import time
from email.utils import parsedate_to_datetime
from pathlib import Path
from xml.etree import ElementTree as ET

import httpx
from tqdm import tqdm

from tifonator.models import Episode, FeedMeta

RSS_URL = "https://feeds.acast.com/public/shows/tifo-football-podcast"

_NS = {
    "itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd",
    "acast": "https://schema.acast.com/1.0/",
}

_TAG_STRIP = re.compile(r"<[^>]+>")


def _text(el: ET.Element, tag: str, ns: str = "") -> str:
    found = el.find(f"{ns}{tag}" if not ns else f"{{{_NS[ns]}}}{tag}")
    if found is None or found.text is None:
        return ""
    return found.text.strip()


def _strip_html(raw: str) -> str:
    return _TAG_STRIP.sub("", raw).strip()


def fetch_feed(url: str = RSS_URL) -> FeedMeta:
    """Fetch the RSS feed and return structured metadata."""
    response = httpx.get(url, follow_redirects=True, timeout=30)
    response.raise_for_status()
    return parse_feed(response.text)


def parse_feed(xml: str) -> FeedMeta:
    """Parse raw RSS XML into a FeedMeta. Testable without network."""
    root = ET.fromstring(xml)
    channel = root.find("channel")
    assert channel is not None

    show_title = _text(channel, "title")
    show_description = _strip_html(_text(channel, "description"))

    episodes: list[Episode] = []
    for item in channel.findall("item"):
        guid_el = item.find("guid")
        guid = guid_el.text.strip() if guid_el is not None and guid_el.text else ""

        title = _text(item, "title")
        pub_date_raw = _text(item, "pubDate")
        pub_date = parsedate_to_datetime(pub_date_raw) if pub_date_raw else None
        if pub_date is None:
            continue

        enclosure = item.find("enclosure")
        if enclosure is None:
            continue
        audio_url = enclosure.get("url", "")
        audio_bytes = int(enclosure.get("length", "0"))

        duration_raw = _text(item, "duration", ns="itunes")
        episode_type = _text(item, "episodeType", ns="itunes") or "full"

        desc_el = item.find("description")
        description = _strip_html(desc_el.text or "") if desc_el is not None else ""

        episodes.append(
            Episode(
                id=guid,
                title=title,
                pub_date=pub_date,
                duration_seconds=duration_raw or "0",
                audio_url=audio_url,
                audio_bytes=audio_bytes,
                description=description,
                episode_type=episode_type,
            )
        )

    return FeedMeta(
        show_title=show_title,
        show_description=show_description,
        episodes=episodes,
    )


def download_episode(episode: Episode, data_dir: Path, *, delay: float = 1.0) -> Path:
    """Download a single episode's audio. Skips if already present."""
    dest = episode.audio_path(data_dir)
    dest.parent.mkdir(parents=True, exist_ok=True)

    if dest.exists() and dest.stat().st_size > 0:
        return dest

    with httpx.stream("GET", episode.audio_url, follow_redirects=True, timeout=60) as r:
        r.raise_for_status()
        total = int(r.headers.get("content-length", episode.audio_bytes or 0))
        with (
            open(dest, "wb") as f,
            tqdm(
                total=total,
                unit="B",
                unit_scale=True,
                desc=episode.title[:50],
                leave=False,
            ) as bar,
        ):
            for chunk in r.iter_bytes(chunk_size=65_536):
                f.write(chunk)
                bar.update(len(chunk))

    time.sleep(delay)
    return dest


def download_all(
    feed: FeedMeta,
    data_dir: Path,
    *,
    limit: int | None = None,
    delay: float = 1.0,
) -> list[Path]:
    """Download all (or up to `limit`) episodes, newest first."""
    episodes = feed.episodes[:limit] if limit else feed.episodes
    paths: list[Path] = []
    for ep in tqdm(episodes, desc="Episodes", unit="ep"):
        paths.append(download_episode(ep, data_dir, delay=delay))
    return paths
