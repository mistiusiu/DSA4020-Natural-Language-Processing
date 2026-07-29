"""
robots.txt handler.

Responsibilities:
    - Fetch robots.txt
    - Cache rules per domain
    - Check URL permissions
    - Extract crawl delay

Uses Python's built-in urllib.robotparser.
"""

from __future__ import annotations

import asyncio
import logging

from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse

from typing import Dict, Optional

import aiohttp


from models import RobotsEntry

from config import (
    USER_AGENT,
    RESPECT_ROBOTS,
)


logger = logging.getLogger(__name__)


class RobotsManager:
    """
    Handles robots.txt checks.

    One instance is shared by the crawler.
    """


    def __init__(self):

        self.cache: Dict[str, RobotsEntry] = {}

        self.parsers: Dict[str, RobotFileParser] = {}

        self.lock = asyncio.Lock()


    ###########################################################################
    # DOMAIN
    ###########################################################################

    def _domain(
        self,
        url: str,
    ) -> str:

        return urlparse(url).netloc


    ###########################################################################
    # FETCH ROBOTS
    ###########################################################################

    async def _load(
        self,
        url: str,
        session: aiohttp.ClientSession,
    ) -> None:

        domain = self._domain(url)

        robots_url = (
            f"{urlparse(url).scheme}://"
            f"{domain}/robots.txt"
        )


        parser = RobotFileParser()

        parser.set_url(
            robots_url
        )


        try:

            async with session.get(
                robots_url,
                timeout=10,
            ) as response:


                if response.status != 200:

                    logger.debug(
                        "No robots.txt: %s",
                        robots_url,
                    )

                    parser.parse([])


                else:

                    content = await response.text()

                    parser.parse(
                        content.splitlines()
                    )


            self.parsers[domain] = parser


            self.cache[domain] = RobotsEntry(
                domain=domain,
                robots_url=robots_url,
                fetched=True,
            )


        except Exception as exc:


            logger.warning(
                "robots.txt failed %s (%s)",
                robots_url,
                exc,
            )


            # Fail open.
            parser.parse([])

            self.parsers[domain] = parser


            self.cache[domain] = RobotsEntry(
                domain=domain,
                robots_url=robots_url,
                fetched=False,
            )


    ###########################################################################
    # CHECK PERMISSION
    ###########################################################################

    async def allowed(
        self,
        url: str,
        session: aiohttp.ClientSession,
    ) -> bool:


        if not RESPECT_ROBOTS:

            return True


        domain = self._domain(url)


        async with self.lock:

            if domain not in self.parsers:

                await self._load(
                    url,
                    session,
                )


        parser = self.parsers[domain]


        try:

            return parser.can_fetch(
                USER_AGENT,
                url,
            )


        except Exception:

            return True



    ###########################################################################
    # CRAWL DELAY
    ###########################################################################

    async def crawl_delay(
        self,
        url: str,
    ) -> Optional[float]:

        domain = self._domain(url)

        parser = self.parsers.get(
            domain
        )


        if not parser:

            return None


        try:

            return parser.crawl_delay(
                USER_AGENT
            )


        except Exception:

            return None
