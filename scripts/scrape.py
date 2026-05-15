"""CLI: scrape all episodes and download audio to data/raw/."""
from tifonator.scrape import RSS_URL

if __name__ == "__main__":
    print(f"Will scrape: {RSS_URL}")
