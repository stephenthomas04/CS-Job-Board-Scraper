"""Scrape public Greenhouse / Lever job boards into a schema-conformant
listings.json.

Flow: fetch -> filter (by title keyword) -> map to schema -> validate -> dedupe
-> sort -> write. The validator (`checkSchema`, `sortListings`) is imported from
the repo-root `current_processor.py` so the scraper and validator can't drift.

Usage:
    pip install -r scraper/requirements.txt
    python scraper/scrape.py
"""

from __future__ import annotations

import html
import json
import os
import re
import sys
import time
from datetime import datetime, timezone

import requests

# Make the repo-root modules importable regardless of the cwd used to launch.
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import config  # noqa: E402  (scraper/config.py)
from current_processor import checkSchema, sortListings  # noqa: E402

ROOT_OUTPUT = os.path.join(REPO_ROOT, "listings.json")
UI_OUTPUT = os.path.join(REPO_ROOT, "ui", "public", "listings.json")

# Current time is used both for date_updated and for season year-rollover.
NOW = datetime.now(timezone.utc)


# --------------------------------------------------------------------------- #
# HTTP
# --------------------------------------------------------------------------- #
def make_session() -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": config.USER_AGENT, "Accept": "application/json"})
    return session


def get_json(session: requests.Session, url: str) -> dict | list | None:
    """GET a URL with a couple of retries. Returns parsed JSON or None on failure."""
    last_err = None
    for attempt in range(config.MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=config.REQUEST_TIMEOUT)
            if resp.status_code == 404:
                return None  # retired/unknown token -> skip gracefully
            resp.raise_for_status()
            return resp.json()
        except (requests.RequestException, ValueError) as exc:
            last_err = exc
            if attempt < config.MAX_RETRIES:
                time.sleep(1.0 * (attempt + 1))
    print(f"    ! request failed for {url}: {last_err}")
    return None


# --------------------------------------------------------------------------- #
# Text helpers
# --------------------------------------------------------------------------- #
_TAG_RE = re.compile(r"<[^>]+>")


def strip_html(raw: str) -> str:
    """Turn an HTML description into lowercase plaintext for phrase matching."""
    if not raw:
        return ""
    text = html.unescape(raw)
    text = _TAG_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def title_matches(title: str) -> bool:
    lowered = title.lower()
    return any(kw in lowered for kw in config.KEYWORDS)


def iso_to_epoch(value: str | None) -> int | None:
    """Parse an ISO-8601 timestamp (optionally with trailing 'Z') to epoch secs."""
    if not value:
        return None
    try:
        cleaned = value.replace("Z", "+00:00")
        return int(datetime.fromisoformat(cleaned).timestamp())
    except (ValueError, TypeError):
        return None


# --------------------------------------------------------------------------- #
# Heuristics: sponsorship + season
# --------------------------------------------------------------------------- #
def infer_sponsorship(description_plain: str) -> str:
    text = description_plain.lower()
    if any(p in text for p in config.CITIZENSHIP_PHRASES):
        return "U.S. Citizenship is Required"
    if any(p in text for p in config.NEGATIVE_PHRASES):
        return "Does Not Offer Sponsorship"
    return ""


# Season within the calendar year, roughly, for year-rollover decisions.
# If the season has clearly already passed this year, roll to next year.
_SEASON_END_MONTH = {"winter": 3, "spring": 6, "summer": 9, "fall": 8}


def infer_season(title: str, description_plain: str) -> str:
    blob = f"{title} {description_plain}".lower()
    is_intern = "intern" in blob
    is_newgrad = any(
        p in blob for p in ("new grad", "new graduate", "entry level", "entry-level", "university graduate")
    )

    if is_intern:
        for season in ("summer", "fall", "spring", "winter"):
            if season in blob:
                year = NOW.year
                # If this season already ended this calendar year, assume next year.
                if NOW.month > _SEASON_END_MONTH[season]:
                    year += 1
                return f"{season.capitalize()} {year}"
        return "Internship"

    if is_newgrad:
        return "New Grad"

    return ""


# --------------------------------------------------------------------------- #
# Mapping
# --------------------------------------------------------------------------- #
def map_greenhouse(job: dict, meta: dict) -> dict:
    description_plain = strip_html(job.get("content", ""))
    date_posted = (
        iso_to_epoch(job.get("first_published"))
        or iso_to_epoch(job.get("updated_at"))
        or int(NOW.timestamp())
    )
    locations = []
    loc = (job.get("location") or {}).get("name")
    if loc:
        locations.append(loc)

    title = job.get("title", "")
    return {
        "source": "greenhouse",
        "company_name": meta["company_name"],
        "company_url": meta["company_url"],
        "id": str(job.get("id", "")),
        "title": title,
        "url": job.get("absolute_url", ""),
        "locations": locations,
        "season": infer_season(title, description_plain),
        "sponsorship": infer_sponsorship(description_plain),
        "active": True,
        "is_visible": True,
        "date_posted": date_posted,
        "date_updated": int(NOW.timestamp()),
    }


def map_lever(job: dict, meta: dict) -> dict:
    description_plain = " ".join(
        filter(None, [job.get("descriptionPlain", ""), job.get("additionalPlain", "")])
    ).strip()
    created = job.get("createdAt")
    date_posted = int(created // 1000) if isinstance(created, (int, float)) else int(NOW.timestamp())

    locations = []
    loc = (job.get("categories") or {}).get("location")
    if loc:
        locations.append(loc)

    title = job.get("text", "")
    return {
        "source": "lever",
        "company_name": meta["company_name"],
        "company_url": meta["company_url"],
        "id": str(job.get("id", "")),
        "title": title,
        "url": job.get("hostedUrl", ""),
        "locations": locations,
        "season": infer_season(title, description_plain),
        "sponsorship": infer_sponsorship(description_plain),
        "active": True,
        "is_visible": True,
        "date_posted": date_posted,
        "date_updated": int(NOW.timestamp()),
    }


# --------------------------------------------------------------------------- #
# Per-board scrape
# --------------------------------------------------------------------------- #
def scrape_greenhouse(session: requests.Session, token: str, meta: dict) -> tuple[list[dict], dict]:
    stats = {"fetched": 0, "kept": 0, "invalid": 0}
    url = f"https://boards-api.greenhouse.io/v1/boards/{token}/jobs?content=true"
    data = get_json(session, url)
    if not data or "jobs" not in data:
        return [], stats

    mapped: list[dict] = []
    for job in data["jobs"]:
        stats["fetched"] += 1
        if not title_matches(job.get("title", "")):
            continue
        obj = map_greenhouse(job, meta)
        errors = checkSchema(obj)
        if errors:
            stats["invalid"] += 1
            print(f"    - dropped invalid greenhouse/{token} listing: {errors[0]}")
            continue
        mapped.append(obj)
        stats["kept"] += 1
    return mapped, stats


def scrape_lever(session: requests.Session, token: str, meta: dict) -> tuple[list[dict], dict]:
    stats = {"fetched": 0, "kept": 0, "invalid": 0}
    url = f"https://api.lever.co/v0/postings/{token}?mode=json"
    data = get_json(session, url)
    if not isinstance(data, list):
        return [], stats

    mapped: list[dict] = []
    for job in data:
        stats["fetched"] += 1
        if not title_matches(job.get("text", "")):
            continue
        obj = map_lever(job, meta)
        errors = checkSchema(obj)
        if errors:
            stats["invalid"] += 1
            print(f"    - dropped invalid lever/{token} listing: {errors[0]}")
            continue
        mapped.append(obj)
        stats["kept"] += 1
    return mapped, stats


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #
def write_outputs(listings: list[dict]) -> None:
    payload = json.dumps(listings, indent=2, ensure_ascii=False)
    with open(ROOT_OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(payload)
    os.makedirs(os.path.dirname(UI_OUTPUT), exist_ok=True)
    with open(UI_OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(payload)


def main() -> int:
    session = make_session()
    all_listings: list[dict] = []
    total_skipped = 0

    print("Scraping Greenhouse boards...")
    for token, meta in config.GREENHOUSE.items():
        listings, stats = scrape_greenhouse(session, token, meta)
        if not listings and stats["fetched"] == 0:
            total_skipped += 1
            print(f"  greenhouse/{token:<20} SKIPPED (404 / no data)")
            continue
        all_listings.extend(listings)
        print(
            f"  greenhouse/{token:<20} fetched={stats['fetched']:<4} "
            f"kept={stats['kept']:<4} invalid={stats['invalid']}"
        )

    print("Scraping Lever boards...")
    for token, meta in config.LEVER.items():
        listings, stats = scrape_lever(session, token, meta)
        if not listings and stats["fetched"] == 0:
            total_skipped += 1
            print(f"  lever/{token:<25} SKIPPED (404 / no data)")
            continue
        all_listings.extend(listings)
        print(
            f"  lever/{token:<25} fetched={stats['fetched']:<4} "
            f"kept={stats['kept']:<4} invalid={stats['invalid']}"
        )

    # Dedupe by (source, id), keeping the first seen.
    seen: set[tuple[str, str]] = set()
    deduped: list[dict] = []
    for job in all_listings:
        key = (job["source"], job["id"])
        if key in seen:
            continue
        seen.add(key)
        deduped.append(job)

    sortListings(deduped)
    write_outputs(deduped)

    print("\n--- Summary ---")
    print(f"  kept (pre-dedupe): {len(all_listings)}")
    print(f"  written (deduped): {len(deduped)}")
    print(f"  boards skipped:    {total_skipped}")
    print(f"  wrote: {ROOT_OUTPUT}")
    print(f"  wrote: {UI_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
