"""
Data models used throughout the PSA crawler.

Using dataclasses keeps the code strongly typed and avoids
passing unstructured dictionaries between modules.
"""

from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional


# ---------------------------------------------------------------------------
# Crawl Task
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class CrawlTask:
    """
    Represents a page waiting to be crawled.
    """

    url: str
    depth: int = 0
    priority: int = 0

    def __lt__(self, other):
        """
        Needed for PriorityQueue.

        Lower values are dequeued first, therefore we
        reverse the comparison so higher priority values
        are visited first.
        """
        return self.priority > other.priority


# ---------------------------------------------------------------------------
# Page Metadata
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class PageMetadata:
    """
    Metadata extracted from a webpage.
    """

    title: str = ""
    description: str = ""
    language: str = ""
    author: str = ""

    published: str = ""
    modified: str = ""

    og_title: str = ""
    og_description: str = ""

    twitter_title: str = ""
    twitter_description: str = ""


# ---------------------------------------------------------------------------
# Heading Record
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class HeadingRecord:
    """
    One extracted heading plus PSA enrichment features.
    """

    website: str

    url: str

    heading_level: str

    heading: str

    # ------------------------------------------------------------------
    # Page metadata
    # ------------------------------------------------------------------

    page_title: str = ""

    meta_description: str = ""

    language: str = ""


    # ------------------------------------------------------------------
    # Context around heading
    # ------------------------------------------------------------------

    previous_heading: str = ""

    next_heading: str = ""

    preceding_text: str = ""

    following_text: str = ""


    # ------------------------------------------------------------------
    # PSA enrichment
    # ------------------------------------------------------------------

    keywords_found: list[str] = field(
        default_factory=list
    )

    organizations: list[str] = field(
        default_factory=list
    )

    dates: list[str] = field(
        default_factory=list
    )

    action_verbs: list[str] = field(
        default_factory=list
    )

    emergency_terms: list[str] = field(
        default_factory=list
    )


    # ------------------------------------------------------------------
    # Scoring
    # ------------------------------------------------------------------

    score: int = 0

    explanations: list[str] = field(
        default_factory=list
    )


    # ------------------------------------------------------------------
    # Crawl metadata
    # ------------------------------------------------------------------

    depth: int = 0

    timestamp: str = field(
        default_factory=lambda:
            datetime.utcnow().isoformat()
    )

    hash: str = ""


    def to_dict(self):
        """
        JSON serialization helper.
        """

        return asdict(self)


# ---------------------------------------------------------------------------
# Crawl Statistics
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class CrawlStats:

    pages_visited: int = 0

    pages_failed: int = 0

    headings_found: int = 0

    duplicate_headings: int = 0

    skipped_urls: int = 0

    robots_blocked: int = 0

    start_time: Optional[datetime] = None

    end_time: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Page
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class ParsedPage:
    """
    Represents a parsed webpage.

    parser.py returns one of these.
    """

    url: str

    metadata: PageMetadata

    headings: List[HeadingRecord]

    links: List[str]

    html: str = ""


# ---------------------------------------------------------------------------
# Robots Cache
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class RobotsEntry:

    domain: str

    robots_url: str

    fetched: bool = False

    allowed_paths: List[str] = field(default_factory=list)

    disallowed_paths: List[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# URL State
# ---------------------------------------------------------------------------

@dataclass(slots=True)
class UrlState:

    url: str

    visited: bool = False

    status_code: int = 0

    retries: int = 0

    timestamp: str = field(
        default_factory=lambda: datetime.utcnow().isoformat()
    )
