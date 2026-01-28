from __future__ import annotations

from typing import List, Dict, Any
import json
import os
import urllib.request
import urllib.error

from .models import Sonnet

POETRYDB_URL = "https://poetrydb.org/author,title/Shakespeare;Sonnet"
CACHE_FILENAME = "sonnets.json"


def module_relative_path(name: str) -> str:
    return os.path.join(os.path.dirname(__file__), name)


class Configuration:
    def __init__(self):
        self.highlight: bool = True
        self.search_mode: str = "AND"     # "AND" or "OR"
        self.hl_mode: str = "DEFAULT"     # "DEFAULT" or "GREEN"

    def copy(self) -> "Configuration":
        c = Configuration()
        c.highlight = self.highlight
        c.search_mode = self.search_mode
        c.hl_mode = self.hl_mode
        return c

    def update(self, other: Dict[str, Any]) -> None:
        if isinstance(other.get("highlight"), bool):
            self.highlight = other["highlight"]

        if other.get("search_mode") in ("AND", "OR"):
            self.search_mode = other["search_mode"]

        if other.get("hl_mode") in ("DEFAULT", "GREEN"):
            self.hl_mode = other["hl_mode"]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "highlight": self.highlight,
            "search_mode": self.search_mode,
            "hl_mode": self.hl_mode,
        }

    def save(self) -> None:
        path = module_relative_path("config.json")
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.to_dict(), f, indent=4)
        except OSError:
            print("Writing config.json failed.")


DEFAULT_CONFIG = Configuration()


def load_config() -> Configuration:
    path = module_relative_path("config.json")
    cfg = DEFAULT_CONFIG.copy()

    try:
        with open(path, "r", encoding="utf-8") as f:
            cfg.update(json.load(f))
    except FileNotFoundError:
        print("No config.json found. Using default configuration.")
    except json.JSONDecodeError:
        print("config.json is invalid. Using default configuration.")
    except OSError:
        print("Could not read config.json. Using default configuration.")

    return cfg


def fetch_sonnets_from_api() -> List[Dict[str, Any]]:
    try:
        with urllib.request.urlopen(POETRYDB_URL, timeout=10) as response:
            status = getattr(response, "status", None)
            if status not in (None, 200):
                raise RuntimeError(f"Request failed with HTTP status {status}")
            return json.load(response)
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError) as exc:
        raise RuntimeError(f"Network-related error occurred: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Failed to decode JSON: {exc}") from exc


def load_sonnets() -> List[Sonnet]:
    path = module_relative_path(CACHE_FILENAME)

    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            print("Loaded sonnets from the cache.")
        except (OSError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Failed to read cache file: {exc}") from exc
    else:
        data = fetch_sonnets_from_api()
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            print("Downloaded sonnets from PoetryDB.")
        except OSError as exc:
            raise RuntimeError(f"Failed to write cache file: {exc}") from exc

    return [Sonnet(d) for d in data]

#xxxx