"""CLI: generate a new episode given a topic."""
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True)
    args = parser.parse_args()
    print(f"Generating episode about: {args.topic}")
