"""One-time converter: legacy listings.json -> new schema.

The legacy data (from the old Simplify/Markdown-table pipeline) uses `terms`
(list) instead of `season` (str) and carries extra `category` / `degrees`
fields with no bearing on the card UI. This maps each legacy row to the schema
defined in `current_processor.py`, validates every row, drops any that can't be
salvaged, sorts, and writes both listings.json and ui/public/listings.json.

Usage:
    python scraper/convert_legacy.py [path/to/legacy.json]
"""

from __future__ import annotations

import json
import os
import sys
import time

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from current_processor import checkSchema, sortListings  # noqa: E402

ROOT_OUTPUT = os.path.join(REPO_ROOT, "listings.json")
UI_OUTPUT = os.path.join(REPO_ROOT, "ui", "public", "listings.json")

# Legacy sponsorship values -> new-schema values. Anything not explicitly a
# negative maps to "" (treated as available/unknown by the UI).
SPONSORSHIP_MAP = {
    "Does Not Offer Sponsorship": "Does Not Offer Sponsorship",
    "U.S. Citizenship is Required": "U.S. Citizenship is Required",
    "Offers Sponsorship": "",
    "Other": "",
    "": "",
}


def to_str(value) -> str:
    return value if isinstance(value, str) else ("" if value is None else str(value))


def to_int(value) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return 0


def convert(row: dict) -> dict:
    terms = row.get("terms")
    season = ""
    if isinstance(terms, list) and terms and isinstance(terms[0], str):
        season = terms[0]

    locations = [loc for loc in (row.get("locations") or []) if isinstance(loc, str)]

    sponsorship = SPONSORSHIP_MAP.get(to_str(row.get("sponsorship")), "")

    return {
        "source": to_str(row.get("source")) or "legacy",
        "company_name": to_str(row.get("company_name")),
        "company_url": to_str(row.get("company_url")),
        "id": to_str(row.get("id")),
        "title": to_str(row.get("title")),
        "url": to_str(row.get("url")),
        "locations": locations,
        "season": season,
        "sponsorship": sponsorship,
        "active": bool(row.get("active", False)),
        "is_visible": bool(row.get("is_visible", True)),
        "date_posted": to_int(row.get("date_posted")),
        "date_updated": to_int(row.get("date_updated")) or int(time.time()),
    }


def main() -> int:
    src = sys.argv[1] if len(sys.argv) > 1 else ROOT_OUTPUT
    with open(src, encoding="utf-8") as fh:
        legacy = json.load(fh)
    print(f"Loaded {len(legacy)} legacy listings from {src}")

    converted: list[dict] = []
    dropped = 0
    for row in legacy:
        obj = convert(row)
        errors = checkSchema(obj)
        if errors:
            dropped += 1
            if dropped <= 5:
                print(f"  - dropped listing {obj.get('id')!r}: {errors[0]}")
            continue
        converted.append(obj)

    sortListings(converted)

    payload = json.dumps(converted, indent=2, ensure_ascii=False)
    with open(ROOT_OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(payload)
    os.makedirs(os.path.dirname(UI_OUTPUT), exist_ok=True)
    with open(UI_OUTPUT, "w", encoding="utf-8") as fh:
        fh.write(payload)

    print("\n--- Summary ---")
    print(f"  converted: {len(converted)}")
    print(f"  dropped:   {dropped}")
    print(f"  wrote: {ROOT_OUTPUT}")
    print(f"  wrote: {UI_OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
