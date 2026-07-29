"""
Asynchronous HTTP fetcher.

Responsible for:
- Connection pooling
- Retries
- Timeouts
- Exponential backoff
- Content-Type validation
- User-Agent handling

No HTML parsing happens here.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

import aiohttp

from config import (
    USER_AGENT,
    REQUEST_TIMEOUT,
    MAX_RETRIES,
    BACKOFF_FACTOR,
    REQUEST_DELAY,
)

from utils import is_html


logger = logging.getLogger(__name__)


class FetchResult:
    """
    Result returned by the Fetcher.
    """

    def __init__(
        self,
        url: str,
        status: int,
        html: Optional[str],
        content_type: str,
    ):
        self.url = url
        self.status = status
        self.html = html
        self.content_type = content_type


class Fetcher:
    """
    Shared asynchronous HTTP client.
    """

    def __init__(self):

        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):

        timeout = aiohttp.ClientTimeout(
            total=REQUEST_TIMEOUT
        )

        connector = aiohttp.TCPConnector(
            limit=100,
            ttl_dns_cache=300,
            ssl=False,
        )

        self.session = aiohttp.ClientSession(
            timeout=timeout,
            connector=connector,
            headers={
                "User-Agent": USER_AGENT,
                "Accept": "text/html",
            },
        )

        return self

    async def __aexit__(
        self,
        exc_type,
        exc,
        tb,
    ):

        if self.session:
            await self.session.close()

    async def fetch(self, url: str) -> Optional[FetchResult]:
        """
        Download one page.

        Returns None if the request ultimately fails.
        """

        for attempt in range(MAX_RETRIES):

            try:

                async with self.session.get(
                    url,
                    allow_redirects=True,
                ) as response:

                    status = response.status

                    content_type = response.headers.get(
                        "Content-Type",
                        "",
                    )

                    if status >= 400:

                        logger.warning(
                            "%s -> HTTP %s",
                            url,
                            status,
                        )

                        raise aiohttp.ClientResponseError(
                            request_info=response.request_info,
                            history=response.history,
                            status=status,
                        )

                    if not is_html(content_type):

                        logger.debug(
                            "Skipping non-HTML %s",
                            url,
                        )

                        return None

                    html = await response.text(
                        errors="ignore"
                    )

                    await asyncio.sleep(
                        REQUEST_DELAY
                    )

                    return FetchResult(
                        url=url,
                        status=status,
                        html=html,
                        content_type=content_type,
                    )

            except (
                aiohttp.ClientError,
                asyncio.TimeoutError,
            ) as exc:

                wait = BACKOFF_FACTOR ** attempt

                logger.warning(
                    "Fetch failed (%s/%s): %s (%s)",
                    attempt + 1,
                    MAX_RETRIES,
                    url,
                    exc,
                )

                await asyncio.sleep(wait)

        logger.error(
            "Giving up on %s",
            url,
        )

        return None

    async def head(self, url: str) -> Optional[int]:
        """
        Lightweight HEAD request.

        Useful for checking large resources before downloading.
        """

        try:

            async with self.session.head(
                url,
                allow_redirects=True,
            ) as response:

                return response.status

        except Exception:

            return None
