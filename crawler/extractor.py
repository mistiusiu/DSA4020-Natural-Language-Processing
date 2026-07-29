"""
Semantic feature extraction for heading records.

This module enriches HeadingRecord objects with information useful
for PSA detection.

Responsibilities:
    - Keyword detection
    - Organization detection
    - Date extraction
    - Emergency indicator detection
    - Action verb detection
    - Heading hashing
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from config import BASE_DIR
from models import HeadingRecord
from utils import heading_hash


###############################################################################
# LOAD KEYWORDS
###############################################################################

KEYWORD_FILE = BASE_DIR / "keywords.json"

with open(KEYWORD_FILE, "r", encoding="utf-8") as f:
    KEYWORDS = json.load(f)

###############################################################################
# REGEXES
###############################################################################

DATE_REGEXES = [

    # 12 January 2025
    re.compile(
        r"\b\d{1,2}\s+"
        r"(January|February|March|April|May|June|July|August|"
        r"September|October|November|December)"
        r"\s+\d{4}\b",
        re.IGNORECASE,
    ),

    # 2025-07-14
    re.compile(
        r"\b\d{4}-\d{2}-\d{2}\b"
    ),

    # 14/07/2025
    re.compile(
        r"\b\d{2}/\d{2}/\d{4}\b"
    ),
]

###############################################################################
# COMMON GOVERNMENT ORGANIZATIONS
###############################################################################

ORGANIZATIONS = [

    "Ministry",

    "Department",

    "Government",

    "County Government",

    "Cabinet",

    "Authority",

    "Commission",

    "Agency",

    "WHO",

    "UNICEF",

    "CDC",

    "Kenya Red Cross",

    "National Treasury",

    "Public Health",
]

###############################################################################
# ACTION VERBS
###############################################################################

ACTION_VERBS = {

    "avoid",

    "report",

    "call",

    "wash",

    "vaccinate",

    "evacuate",

    "stay",

    "remain",

    "seek",

    "visit",

    "register",

    "apply",

    "protect",

    "monitor",

    "wear",

    "prepare",

    "boil",

    "notify",

    "observe",
}

###############################################################################
# EMERGENCY WORDS
###############################################################################

EMERGENCY_WORDS = {

    "outbreak",

    "warning",

    "emergency",

    "danger",

    "alert",

    "flood",

    "drought",

    "earthquake",

    "cyclone",

    "cholera",

    "covid",

    "ebola",

    "fire",

    "security",
}

###############################################################################
# HELPERS
###############################################################################

def _combined_text(record: HeadingRecord) -> str:
    return " ".join(
        [
            record.heading,
            record.preceding_text,
            record.following_text,
            record.page_title,
            record.meta_description,
        ]
    )


###############################################################################
# KEYWORDS
###############################################################################

def extract_keywords(record: HeadingRecord) -> list[str]:

    text = _combined_text(record).lower()

    found = []

    for category in KEYWORDS.values():

        for keyword in category:

            if keyword.lower() in text:

                found.append(keyword)

    return sorted(set(found))


###############################################################################
# ORGANIZATIONS
###############################################################################

def extract_organizations(record: HeadingRecord) -> list[str]:

    text = _combined_text(record)

    found = []

    for org in ORGANIZATIONS:

        if org.lower() in text.lower():

            found.append(org)

    return found


###############################################################################
# DATES
###############################################################################

def extract_dates(record: HeadingRecord) -> list[str]:

    text = _combined_text(record)

    matches = []

    for regex in DATE_REGEXES:

        matches.extend(regex.findall(text))

    return matches


###############################################################################
# ACTION VERBS
###############################################################################

def extract_action_verbs(record: HeadingRecord) -> list[str]:

    text = _combined_text(record).lower()

    found = []

    for verb in ACTION_VERBS:

        if verb in text:

            found.append(verb)

    return sorted(found)


###############################################################################
# EMERGENCY TERMS
###############################################################################

def extract_emergency_terms(record: HeadingRecord) -> list[str]:

    text = _combined_text(record).lower()

    found = []

    for word in EMERGENCY_WORDS:

        if word in text:

            found.append(word)

    return sorted(found)


###############################################################################
# ENRICHMENT
###############################################################################

def enrich(record: HeadingRecord) -> HeadingRecord:
    """
    Add semantic information to a HeadingRecord.
    """

    record.keywords_found = extract_keywords(record)

    record.hash = heading_hash(
        record.heading,
        record.preceding_text,
        record.following_text,
    )

    # Attach dynamic attributes.
    # (We'll later move these into HeadingRecord if desired.)

    record.organizations = extract_organizations(record)

    record.dates = extract_dates(record)

    record.action_verbs = extract_action_verbs(record)

    record.emergency_terms = extract_emergency_terms(record)

    return record
