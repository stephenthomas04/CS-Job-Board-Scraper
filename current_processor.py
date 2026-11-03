"""Schema validation and sorting for job listings.

This module is the single source of truth for the listings schema. Both the
scraper (`scraper/scrape.py`) and any data-conversion utilities import
`checkSchema` and `sortListings` from here so the pipeline and the validator can
never drift apart.

Schema (every key required):
    source        str        e.g. "greenhouse", "lever", "Simplify"
    company_name  str
    company_url   str
    id            str
    title         str
    url           str
    locations     list[str]
    season        str        e.g. "Summer 2026", "New Grad", "" (unknown)
    sponsorship   str        "" | "Does Not Offer Sponsorship"
                             | "U.S. Citizenship is Required"
    active        bool
    is_visible    bool
    date_posted   int        epoch seconds
    date_updated  int        epoch seconds
"""

from __future__ import annotations

# key -> expected python type(s). bool must be checked before int because in
# Python `bool` is a subclass of `int` (isinstance(True, int) is True).
SCHEMA: dict[str, type | tuple[type, ...]] = {
    "source": str,
    "company_name": str,
    "company_url": str,
    "id": str,
    "title": str,
    "url": str,
    "locations": list,
    "season": str,
    "sponsorship": str,
    "active": bool,
    "is_visible": bool,
    "date_posted": int,
    "date_updated": int,
}

VALID_SPONSORSHIP = {
    "",
    "Does Not Offer Sponsorship",
    "U.S. Citizenship is Required",
}


class SchemaError(Exception):
    """Raised when a listing (or batch) fails schema validation.

    Carries the list of individual error strings so callers can either surface
    them all or fail fast.
    """

    def __init__(self, errors: list[str]):
        self.errors = errors
        super().__init__("; ".join(errors) if errors else "schema validation failed")


def _type_name(expected: type | tuple[type, ...]) -> str:
    if isinstance(expected, tuple):
        return " or ".join(t.__name__ for t in expected)
    return expected.__name__


def checkSchema(job: dict) -> list[str]:
    """Validate a single listing dict.

    Returns a list of human-readable error strings. An empty list means the
    listing is valid.
    """
    errors: list[str] = []

    if not isinstance(job, dict):
        return [f"listing is not an object (got {type(job).__name__})"]

    ident = job.get("id", "<no id>")

    for key, expected in SCHEMA.items():
        if key not in job:
            errors.append(f"[{ident}] missing required key '{key}'")
            continue

        value = job[key]

        # bool is a subclass of int, so reject bools where an int is expected
        # and reject ints where a bool is expected.
        if expected is int and isinstance(value, bool):
            errors.append(f"[{ident}] key '{key}' should be int, got bool")
            continue
        if expected is bool and not isinstance(value, bool):
            errors.append(
                f"[{ident}] key '{key}' should be bool, got {type(value).__name__}"
            )
            continue

        if not isinstance(value, expected):
            errors.append(
                f"[{ident}] key '{key}' should be {_type_name(expected)}, "
                f"got {type(value).__name__}"
            )
            continue

        # locations must be a list of strings.
        if key == "locations":
            for i, loc in enumerate(value):
                if not isinstance(loc, str):
                    errors.append(
                        f"[{ident}] locations[{i}] should be str, "
                        f"got {type(loc).__name__}"
                    )

    # sponsorship must be one of the known values.
    if isinstance(job.get("sponsorship"), str) and job["sponsorship"] not in VALID_SPONSORSHIP:
        errors.append(
            f"[{ident}] sponsorship '{job['sponsorship']}' is not one of "
            f"{sorted(VALID_SPONSORSHIP)}"
        )

    return errors


def validateAll(listings: list[dict], *, raise_on_error: bool = False) -> list[str]:
    """Validate a list of listings. Returns the flattened list of all errors.

    If ``raise_on_error`` is True and any listing is invalid, raises SchemaError.
    """
    all_errors: list[str] = []
    for job in listings:
        all_errors.extend(checkSchema(job))
    if all_errors and raise_on_error:
        raise SchemaError(all_errors)
    return all_errors


def sortListings(listings: list[dict]) -> list[dict]:
    """Sort listings by date_posted desc, tie-broken by date_updated desc.

    Sorts in place and also returns the list for convenience.
    """
    listings.sort(
        key=lambda j: (j.get("date_posted", 0), j.get("date_updated", 0)),
        reverse=True,
    )
    return listings
