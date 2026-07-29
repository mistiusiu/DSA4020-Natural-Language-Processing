"""
Persistent crawl state manager.

Stores:
    - visited URLs
    - failed URLs
    - retry counts
    - HTTP status
    - timestamps

Uses JSON persistence.

For very large crawls (>1M URLs), this can later be
replaced with SQLite.
"""

from __future__ import annotations

import json
import asyncio
import logging

from pathlib import Path

from typing import Dict, Optional

from datetime import datetime


from models import UrlState

from config import STATE_FILE


logger = logging.getLogger(__name__)


class StateManager:
    """
    Handles crawl persistence.
    """


    def __init__(
        self,
        filepath: Path = STATE_FILE,
    ):

        self.filepath = filepath

        self.urls: Dict[str, UrlState] = {}

        self.lock = asyncio.Lock()



    ###########################################################################
    # LOAD
    ###########################################################################

    async def load(self):

        if not self.filepath.exists():

            logger.info(
                "No previous crawl state found"
            )

            return


        try:

            with open(
                self.filepath,
                "r",
                encoding="utf-8",
            ) as f:

                data = json.load(f)


            for url, value in data.items():

                self.urls[url] = UrlState(
                    **value
                )


            logger.info(
                "Loaded %s URLs",
                len(self.urls),
            )


        except Exception as exc:

            logger.error(
                "Failed loading state: %s",
                exc,
            )



    ###########################################################################
    # SAVE
    ###########################################################################

    async def save(self):

        async with self.lock:


            data = {

                url: {

                    "url": state.url,

                    "visited": state.visited,

                    "status_code": state.status_code,

                    "retries": state.retries,

                    "timestamp": state.timestamp,

                }

                for url, state in self.urls.items()

            }


            self.filepath.parent.mkdir(
                parents=True,
                exist_ok=True,
            )


            temp = (
                self.filepath
                .with_suffix(".tmp")
            )


            with open(
                temp,
                "w",
                encoding="utf-8",
            ) as f:

                json.dump(
                    data,
                    f,
                    indent=2,
                )


            # Atomic replacement.
            temp.replace(
                self.filepath
            )


    ###########################################################################
    # CHECK VISITED
    ###########################################################################

    def visited(
        self,
        url: str,
    ) -> bool:

        state = self.urls.get(url)

        return (
            state is not None
            and state.visited
        )



    ###########################################################################
    # MARK SUCCESS
    ###########################################################################

    async def mark_success(
        self,
        url: str,
        status_code: int,
    ):


        self.urls[url] = UrlState(

            url=url,

            visited=True,

            status_code=status_code,

            retries=0,

            timestamp=datetime.utcnow()
                .isoformat(),

        )


    ###########################################################################
    # MARK FAILURE
    ###########################################################################

    async def mark_failure(
        self,
        url: str,
    ):


        existing = self.urls.get(
            url
        )


        retries = 1


        if existing:

            retries = (
                existing.retries + 1
            )


        self.urls[url] = UrlState(

            url=url,

            visited=False,

            status_code=0,

            retries=retries,

            timestamp=datetime.utcnow()
                .isoformat(),

        )



    ###########################################################################
    # STATISTICS
    ###########################################################################

    def stats(self):

        total = len(self.urls)

        visited = sum(
            1
            for x in self.urls.values()
            if x.visited
        )


        failed = sum(
            1
            for x in self.urls.values()
            if not x.visited
        )


        return {

            "total": total,

            "visited": visited,

            "failed": failed,

        }
