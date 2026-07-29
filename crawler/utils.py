"""
General utility functions for the PSA crawler.

These functions should be stateless and free of side effects.
"""

from __future__ import annotations

import hashlib
import posixpath
import re
import json
import csv

from pathlib import Path
from typing import List, Dict
from urllib.parse import (
    urljoin,
    urlparse,
    urlunparse,
    parse_qsl,
    urlencode,
)

from config import (
    SKIP_EXTENSIONS,
    SKIP_PATHS,
    URL_PRIORITY_KEYWORDS,
)

###############################################################################
# URL NORMALIZATION
###############################################################################

TRACKING_PARAMETERS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "utm_id",
    "fbclid",
    "gclid",
    "msclkid",
}


def normalize_url(url: str, base_url: str | None = None) -> str:
    """
    Convert URLs into a canonical representation.

    - Resolves relative URLs.
    - Removes fragments.
    - Removes tracking parameters.
    - Removes duplicate slashes.
    - Removes trailing slash (except root).
    """

    if base_url:
        url = urljoin(base_url, url)

    parsed = urlparse(url)

    query = urlencode(
        sorted(
            [
                (k, v)
                for k, v in parse_qsl(parsed.query)
                if k.lower() not in TRACKING_PARAMETERS
            ]
        )
    )

    path = posixpath.normpath(parsed.path)

    if path == ".":
        path = "/"

    normalized = parsed._replace(
        fragment="",
        query=query,
        path=path,
    )

    url = urlunparse(normalized)

    if url.endswith("/") and path != "/":
        url = url[:-1]

    return url


###############################################################################
# DOMAIN HELPERS
###############################################################################

def get_domain(url: str) -> str:
    return urlparse(url).netloc.lower()


def same_domain(url: str, domain: str) -> bool:
    return get_domain(url) == domain.lower()


###############################################################################
# FILTERING
###############################################################################

def should_skip_url(url: str) -> bool:
    """
    Skip binary files and admin pages.
    """

    parsed = urlparse(url)

    path = parsed.path.lower()

    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return True

    for fragment in SKIP_PATHS:
        if fragment in path:
            return True

    return False


###############################################################################
# URL PRIORITY
###############################################################################

def calculate_priority(url: str) -> int:
    """
    Higher score = crawled earlier.
    """

    score = 0

    lower = url.lower()

    for word in URL_PRIORITY_KEYWORDS:

        if word in lower:
            score += 10

    if "/news" in lower:
        score += 20

    if "/press" in lower:
        score += 20

    if "/media" in lower:
        score += 20

    if "/announcement" in lower:
        score += 30

    if "/notice" in lower:
        score += 30

    return score


###############################################################################
# TEXT CLEANING
###############################################################################

_whitespace = re.compile(r"\s+")


def clean_text(text: str) -> str:
    """
    Collapse whitespace.

    HTML often contains
    newlines
    tabs

    etc.
    """

    text = _whitespace.sub(" ", text)

    return text.strip()


###############################################################################
# HASHING
###############################################################################

def heading_hash(
    heading: str,
    preceding: str,
    following: str,
) -> str:
    """
    Stable SHA256 hash used for duplicate detection.
    """

    text = "|".join(
        [
            clean_text(heading),
            clean_text(preceding),
            clean_text(following),
        ]
    )

    return hashlib.sha256(
        text.encode("utf-8")
    ).hexdigest()


###############################################################################
# HTML HELPERS
###############################################################################

def is_html(content_type: str | None) -> bool:

    if not content_type:
        return False

    return "text/html" in content_type.lower()


###############################################################################
# URL VALIDATION
###############################################################################

def is_valid_http_url(url: str) -> bool:

    parsed = urlparse(url)

    return parsed.scheme in {"http", "https"}


###############################################################################
# SAFE STRING
###############################################################################

def truncate(text: str, length: int = 250) -> str:
    """
    Prevent excessively large JSON records.
    """

    text = clean_text(text)

    if len(text) <= length:
        return text

    return text[: length - 3] + "..."


def load_jsonl(file_path: str) -> List[Dict]:
    """
    Load a JSON Lines file into a list of dictionaries.
    Each line must contain a valid JSON object.
    """
    records = []

    path = Path(file_path)

    with path.open("r", encoding="utf-8") as file:
        for line_number, line in enumerate(file, start=1):
            line = line.strip()

            if not line:
                continue

            try:
                records.append(json.loads(line))

            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"Invalid JSON on line {line_number}: {exc}"
                )

    return records


def save_json(data: List[Dict], file_path: str):
    """
    Save records as formatted JSON.
    """
    path = Path(file_path)

    with path.open("w", encoding="utf-8") as file:
        json.dump(
            data,
            file,
            indent=4,
            ensure_ascii=False
        )


def save_csv(data: List[Dict], file_path: str):
    """
    Save records as CSV.
    Handles nested lists by converting them to strings.
    """

    if not data:
        return

    path = Path(file_path)

    # Get all keys dynamically
    fields = set()

    for item in data:
        fields.update(item.keys())

    fields = sorted(fields)

    with path.open(
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fields
        )

        writer.writeheader()

        for item in data:
            row = {}

            for key in fields:
                value = item.get(key, "")

                if isinstance(value, list):
                    value = ", ".join(map(str, value))

                elif isinstance(value, dict):
                    value = json.dumps(value)

                row[key] = value

            writer.writerow(row)


def sort_by_score(
    records: List[Dict],
    descending: bool = True
) -> List[Dict]:
    """
    Sort records by score.
    """

    return sorted(
        records,
        key=lambda x: x.get("score", 0),
        reverse=descending
    )
