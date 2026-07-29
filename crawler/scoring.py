"""
Configurable PSA scoring engine.

The scoring rules are loaded externally from JSON.
This allows country-specific tuning without modifying code.
"""

from __future__ import annotations

import json
from pathlib import Path

from dataclasses import dataclass, field

from models import HeadingRecord

from config import BASE_DIR


###############################################################################
# LOAD RULES
###############################################################################

RULE_FILE = BASE_DIR / "scoring_rules.json"


with open(
    RULE_FILE,
    "r",
    encoding="utf-8",
) as f:

    RULES = json.load(f)


WEIGHTS = RULES["weights"]

HEADING_PATTERNS = RULES["heading_patterns"]

GOVERNMENT_DOMAINS = tuple(
    RULES["government_domains"]
)

MAX_SCORE = RULES["score_limits"]["maximum"]


###############################################################################
# RESULT OBJECT
###############################################################################

@dataclass
class ScoreResult:

    score: int = 0

    reasons: list[str] = field(
        default_factory=list
    )


###############################################################################
# SCORER
###############################################################################

class Scorer:

    def score(
        self,
        record: HeadingRecord,
    ) -> ScoreResult:


        result = ScoreResult()


        heading = record.heading.lower()


        #######################################################################
        # Heading patterns
        #######################################################################

        for pattern, weight in HEADING_PATTERNS.items():

            if pattern.lower() in heading:

                result.score += weight

                result.reasons.append(
                    f"+{weight} Heading pattern '{pattern}'"
                )


        #######################################################################
        # Extracted keywords
        #######################################################################

        for keyword in record.keywords_found:

            weight = WEIGHTS["keyword"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Keyword '{keyword}'"
            )


        #######################################################################
        # Emergency indicators
        #######################################################################

        for term in record.emergency_terms:

            weight = WEIGHTS["emergency_term"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Emergency term '{term}'"
            )


        #######################################################################
        # Action verbs
        #######################################################################

        for verb in record.action_verbs:

            weight = WEIGHTS["action_verb"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Action '{verb}'"
            )


        #######################################################################
        # Organizations
        #######################################################################

        for org in record.organizations:

            weight = WEIGHTS["organization"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Organization '{org}'"
            )


        #######################################################################
        # Dates
        #######################################################################

        if record.dates:

            weight = WEIGHTS["date_detected"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Date detected"
            )


        #######################################################################
        # H1 headings
        #######################################################################

        if record.heading_level == "H1":

            weight = WEIGHTS["h1_heading"]

            result.score += weight

            result.reasons.append(
                f"+{weight} H1 heading"
            )


        #######################################################################
        # Context quality
        #######################################################################

        if len(record.following_text) > 200:

            weight = WEIGHTS["rich_context"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Rich context"
            )


        #######################################################################
        # Government domains
        #######################################################################

        domain = record.website.lower()

        if domain.endswith(
            GOVERNMENT_DOMAINS
        ):

            weight = WEIGHTS["government_domain"]

            result.score += weight

            result.reasons.append(
                f"+{weight} Government domain"
            )


        #######################################################################
        # Limit
        #######################################################################

        result.score = min(
            result.score,
            MAX_SCORE
        )


        return result



###############################################################################
# Convenience wrapper
###############################################################################

def score_record(
    record: HeadingRecord,
) -> HeadingRecord:

    result = Scorer().score(record)

    record.score = result.score

    record.explanations = result.reasons

    return record
