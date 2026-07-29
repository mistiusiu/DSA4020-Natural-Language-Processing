"""
HTML parser.

Responsible for converting raw HTML into a ParsedPage object.

No networking or crawling logic belongs here.
"""

from __future__ import annotations

from bs4 import BeautifulSoup, Tag
from urllib.parse import urljoin

from config import (
    HEADING_TAGS,
    FOLLOWING_PARAGRAPHS,
)

from models import (
    ParsedPage,
    PageMetadata,
    HeadingRecord,
)

from utils import (
    normalize_url,
    clean_text,
)


###############################################################################
# META HELPERS
###############################################################################

def _meta_content(soup: BeautifulSoup, name: str) -> str:
    """
    Read a standard meta tag.
    """

    tag = soup.find("meta", attrs={"name": name})

    if tag:
        return clean_text(tag.get("content", ""))

    return ""


def _property_content(soup: BeautifulSoup, prop: str) -> str:
    """
    Read OpenGraph tags.
    """

    tag = soup.find("meta", attrs={"property": prop})

    if tag:
        return clean_text(tag.get("content", ""))

    return ""


###############################################################################
# METADATA
###############################################################################

def extract_metadata(soup: BeautifulSoup) -> PageMetadata:

    title = ""

    if soup.title:
        title = clean_text(soup.title.get_text())

    html = soup.find("html")

    language = ""

    if html:
        language = html.get("lang", "")

    return PageMetadata(
        title=title,
        description=_meta_content(
            soup,
            "description",
        ),
        language=language,
        author=_meta_content(
            soup,
            "author",
        ),
        published=_property_content(
            soup,
            "article:published_time",
        ),
        modified=_property_content(
            soup,
            "article:modified_time",
        ),
        og_title=_property_content(
            soup,
            "og:title",
        ),
        og_description=_property_content(
            soup,
            "og:description",
        ),
        twitter_title=_meta_content(
            soup,
            "twitter:title",
        ),
        twitter_description=_meta_content(
            soup,
            "twitter:description",
        ),
    )


###############################################################################
# LINKS
###############################################################################

def extract_links(
    soup: BeautifulSoup,
    current_url: str,
) -> list[str]:

    links = []

    for tag in soup.find_all("a", href=True):

        href = normalize_url(
            tag["href"],
            current_url,
        )

        links.append(href)

    return list(dict.fromkeys(links))


###############################################################################
# CONTEXT
###############################################################################

def _previous_heading(tag: Tag) -> str:

    previous = tag.find_previous(
        HEADING_TAGS
    )

    if previous:

        return clean_text(
            previous.get_text()
        )

    return ""


def _next_heading(tag: Tag) -> str:

    nxt = tag.find_next(
        HEADING_TAGS
    )

    if nxt:

        return clean_text(
            nxt.get_text()
        )

    return ""


def _preceding_text(tag: Tag) -> str:
    """
    Previous paragraph.
    """

    previous = tag.find_previous("p")

    if previous:

        return clean_text(
            previous.get_text()
        )

    return ""


def _following_text(tag: Tag) -> str:
    """
    Collect one or more following paragraphs.
    """

    paragraphs = []

    node = tag

    while len(paragraphs) < FOLLOWING_PARAGRAPHS:

        node = node.find_next()

        if node is None:
            break

        if not isinstance(node, Tag):
            continue

        if node.name in HEADING_TAGS:
            break

        if node.name == "p":

            text = clean_text(
                node.get_text()
            )

            if text:
                paragraphs.append(text)

    return "\n\n".join(paragraphs)


###############################################################################
# HEADINGS
###############################################################################

def extract_headings(
    soup: BeautifulSoup,
    metadata: PageMetadata,
    url: str,
) -> list[HeadingRecord]:

    headings = []

    domain = url.split("/")[2]

    for level in HEADING_TAGS:

        for tag in soup.find_all(level):

            heading = clean_text(
                tag.get_text()
            )

            if not heading:
                continue

            headings.append(
                HeadingRecord(
                    website=domain,
                    url=url,
                    heading_level=level.upper(),
                    heading=heading,
                    page_title=metadata.title,
                    meta_description=metadata.description,
                    language=metadata.language,
                    previous_heading=_previous_heading(tag),
                    next_heading=_next_heading(tag),
                    preceding_text=_preceding_text(tag),
                    following_text=_following_text(tag),
                )
            )

    return headings


###############################################################################
# MAIN PARSER
###############################################################################

def parse_html(
    url: str,
    html: str,
) -> ParsedPage:
    """
    Convert raw HTML into structured data.
    """

    soup = BeautifulSoup(
        html,
        "lxml",
    )

    metadata = extract_metadata(
        soup,
    )

    headings = extract_headings(
        soup,
        metadata,
        url,
    )

    links = extract_links(
        soup,
        url,
    )

    return ParsedPage(
        url=url,
        metadata=metadata,
        headings=headings,
        links=links,
        html="",
    )
