"""Contract tests: assert that parse_feed() produces well-typed Episode objects.

These run without network access. The fixture XML mirrors the real feed shape.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from tifonator.models import Episode, FeedMeta
from tifonator.scrape import parse_feed

FIXTURE_XML = textwrap.dedent("""\
    <?xml version="1.0" encoding="utf-8"?>
    <rss version="2.0"
         xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
         xmlns:acast="https://schema.acast.com/1.0/">
      <channel>
        <title>Tifo Football Podcast</title>
        <description><![CDATA[In-depth tactical breakdowns.]]></description>
        <item>
          <guid isPermaLink="false">abc123</guid>
          <title><![CDATA[The False Nine Explained]]></title>
          <pubDate>Thu, 14 May 2026 16:52:05 GMT</pubDate>
          <itunes:duration>1:04:10</itunes:duration>
          <enclosure url="https://example.com/ep1.mp3" length="92409183" type="audio/mpeg"/>
          <itunes:episodeType>full</itunes:episodeType>
          <description><![CDATA[<p>A deep dive into the false nine position.</p>]]></description>
        </item>
        <item>
          <guid isPermaLink="false">def456</guid>
          <title>Short Episode</title>
          <pubDate>Tue, 12 May 2026 02:00:00 GMT</pubDate>
          <itunes:duration>57:17</itunes:duration>
          <enclosure url="https://example.com/ep2.mp3" length="82556753" type="audio/mpeg"/>
          <itunes:episodeType>full</itunes:episodeType>
          <description>Plain text description.</description>
        </item>
      </channel>
    </rss>
""")


@pytest.fixture()
def feed() -> FeedMeta:
    return parse_feed(FIXTURE_XML)


def test_given_valid_xml_when_parsed_then_returns_feedmeta(feed: FeedMeta) -> None:
    assert isinstance(feed, FeedMeta)
    assert feed.show_title == "Tifo Football Podcast"


def test_given_valid_xml_when_parsed_then_all_episodes_are_typed(feed: FeedMeta) -> None:
    assert len(feed.episodes) == 2
    for ep in feed.episodes:
        assert isinstance(ep, Episode)


def test_given_hms_duration_when_parsed_then_converts_to_seconds(feed: FeedMeta) -> None:
    # 1:04:10 = 3600 + 240 + 10 = 3850
    assert feed.episodes[0].duration_seconds == 3850


def test_given_mm_ss_duration_when_parsed_then_converts_to_seconds(feed: FeedMeta) -> None:
    # 57:17 = 3437
    assert feed.episodes[1].duration_seconds == 3437


def test_given_html_description_when_parsed_then_strips_tags(feed: FeedMeta) -> None:
    assert "<p>" not in feed.episodes[0].description
    assert "false nine" in feed.episodes[0].description


def test_given_episode_when_pub_date_parsed_then_is_timezone_aware(feed: FeedMeta) -> None:
    for ep in feed.episodes:
        assert ep.pub_date.tzinfo is not None


def test_given_episode_when_audio_path_resolved_then_uses_id(
    feed: FeedMeta, tmp_path: Path
) -> None:
    ep = feed.episodes[0]
    path = ep.audio_path(tmp_path)
    assert path == tmp_path / "raw" / "abc123.mp3"


def test_given_episode_when_transcript_path_resolved_then_uses_id(
    feed: FeedMeta, tmp_path: Path
) -> None:
    ep = feed.episodes[0]
    path = ep.transcript_path(tmp_path)
    assert path == tmp_path / "transcripts" / "abc123.txt"


@pytest.mark.integration
def test_given_live_feed_when_fetched_then_returns_episodes() -> None:
    """Hits the real feed — skipped by default, run with: pytest -m integration"""
    from tifonator.scrape import fetch_feed

    feed = fetch_feed()
    assert len(feed.episodes) > 0
    assert all(ep.audio_url.startswith("https://") for ep in feed.episodes)
    assert all(ep.duration_seconds > 0 for ep in feed.episodes)
