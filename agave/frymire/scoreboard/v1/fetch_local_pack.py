#!/usr/bin/env python3
"""Fetch Google local/map pack results for Frymire territory-defense query set."""

from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

DIR = Path(__file__).resolve().parent
QUERIES_PATH = DIR / "queries.json"
RESULTS_PATH = DIR / "results.json"

ENV_KEYS = (
    "VALUESERP_API_KEY",
    "VALUE_SERP_API_KEY",
    "VALUESERP_KEY",
    "SERPWOW_API_KEY",
    "TRAJECT_API_KEY",
)

API_ENDPOINTS = (
    "https://api.valueserp.com/search",
    "https://api.serpwow.com/live/search",
)

GIANT_PATTERNS = {
    "Baker Brothers": re.compile(r"baker\s*brothers?", re.I),
    "Berkeys": re.compile(r"berkeys?", re.I),
    "Rescue Air": re.compile(r"rescue\s*air", re.I),
}
FRYMIRE_PATTERN = re.compile(r"frymire", re.I)


def resolve_api_key() -> tuple[str, str]:
    for name in ENV_KEYS:
        value = os.environ.get(name, "").strip()
        if value:
            return value, name
    raise SystemExit(
        "No API key found. Set one of: " + ", ".join(ENV_KEYS)
    )


def fetch_places(api_key: str, query: str, location: str) -> tuple[dict, str]:
    params = {
        "api_key": api_key,
        "search_type": "places",
        "q": query,
        "location": location,
        "engine": "google",
    }
    last_error = ""
    for base in API_ENDPOINTS:
        url = f"{base}?{urllib.parse.urlencode(params)}"
        req = urllib.request.Request(url, headers={"User-Agent": "frymire-scoreboard/1"})
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                data = json.loads(resp.read().decode())
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
            continue
        info = data.get("request_info", {})
        if info.get("success"):
            provider = "valueserp" if "valueserp" in base else "serpwow"
            return data, provider
        last_error = info.get("message", "unknown error")
        if "not valid" in last_error.lower():
            continue
        raise RuntimeError(last_error)
    raise RuntimeError(last_error or "all endpoints failed")


def match_brand(title: str) -> str | None:
    if FRYMIRE_PATTERN.search(title):
        return "Frymire"
    for name, pattern in GIANT_PATTERNS.items():
        if pattern.search(title):
            return name
    return None


def summarize_places(places: list[dict], top_n: int = 5) -> dict:
    leaders = []
    frymire_pos = None
    giant_positions: dict[str, int] = {}
    for place in places[:top_n]:
        title = place.get("title", "")
        pos = place.get("position")
        brand = match_brand(title)
        leaders.append(
            {
                "position": pos,
                "title": title,
                "rating": place.get("rating"),
                "reviews": place.get("reviews"),
                "brand": brand,
            }
        )
        if brand == "Frymire" and frymire_pos is None:
            frymire_pos = pos
        if brand and brand != "Frymire" and brand not in giant_positions:
            giant_positions[brand] = pos
    giants_in_pack = bool(giant_positions)
    frymire_in_pack = frymire_pos is not None
    if giants_in_pack and not frymire_in_pack:
        encroachment = "high"
    elif giants_in_pack and frymire_in_pack and frymire_pos and frymire_pos > 3:
        encroachment = "medium"
    elif giants_in_pack and frymire_in_pack and frymire_pos and frymire_pos <= 3:
        encroachment = "watch"
    elif not frymire_in_pack:
        encroachment = "high"
    else:
        encroachment = "watch"
    return {
        "leaders": leaders,
        "frymire_position": frymire_pos,
        "giant_positions": giant_positions,
        "encroachment": encroachment,
    }


def main() -> None:
    api_key, key_name = resolve_api_key()
    queries_doc = json.loads(QUERIES_PATH.read_text())
    fetched_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    results: list[dict] = []
    provider = None
    credits_used = 0

    for i, item in enumerate(queries_doc["queries"]):
        if i > 0:
            time.sleep(1.5)
        print(f"Fetching {item['id']}: {item['q']}", file=sys.stderr)
        data, provider = fetch_places(api_key, item["q"], item["location"])
        credits_used += data.get("request_info", {}).get("credits_used_this_request", 1)
        places = data.get("places_results") or []
        summary = summarize_places(places)
        results.append(
            {
                **item,
                "fetched_at": fetched_at,
                "provider": provider,
                "engine_url": data.get("search_metadata", {}).get("engine_url"),
                **summary,
            }
        )

    output = {
        "fetched_at": fetched_at,
        "api_key_env": key_name,
        "provider": provider,
        "credits_used": credits_used,
        "query_count": len(results),
        "giants": queries_doc["giants"],
        "results": results,
    }
    RESULTS_PATH.write_text(json.dumps(output, indent=2) + "\n")
    print(f"Wrote {RESULTS_PATH} ({len(results)} queries, {credits_used} credits)", file=sys.stderr)


if __name__ == "__main__":
    main()
