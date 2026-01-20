#!/usr/bin/env python3
"""
Part 11 starter.

WHAT'S NEW IN PART 11. A positional Index. It's almost done, only the finishing touches remain.
"""
from typing import List
import time

from .constants import BANNER, HELP
from .models import SearchResult, Searcher

from .file_utilities import load_config, load_sonnets, Configuration

# New import from Part 10
from .settings_command_module import SettingsCommand


def print_results(query: str, results: List[SearchResult], highlight_mode: str | None, elapsed_ms: float):
    total_docs = len(results)
    print(f"\nQuery: {query!r}")
    print(f"Matches: {total_docs} sonnet(s)  |  time: {elapsed_ms:.2f} ms")

    for idx, r in enumerate(results, start=1):
        r.print(idx, highlight_mode, total_docs)


def main():
    print(BANNER)

    config: Configuration = load_config()
    sonnets = load_sonnets()
    searcher = Searcher(sonnets)

    settings_cmd = SettingsCommand(config)

    while True:
        raw = input("\n> ").strip()

        if raw == "":
            continue

        if raw == ":quit":
            print("Bye.")
            break

        if raw == ":help":
            print(HELP)
            continue

        # Settings commands (Part 10)
        if raw.startswith(":"):
            settings_cmd.execute(raw)
            continue

        # Search
        start = time.perf_counter()

        results = searcher.search(raw, config.search_mode)

        # Initialize elapsed_ms to contain the number of milliseconds the query evaluation took
        elapsed_ms = (time.perf_counter() - start) * 1000

        highlight_mode = config.hl_mode if config.highlight else None

        print_results(raw, results, highlight_mode, elapsed_ms)

    if __name__ == "__main__":
        main()

if __name__ == "__main__":
    main()
