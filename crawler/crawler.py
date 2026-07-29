"""
Main PSA crawler.

Pipeline:

URL Queue
    |
    v
Robots Check
    |
    v
Fetcher
    |
    v
Parser
    |
    v
Extractor
    |
    v
Scoring
    |
    v
JSONL Writer
"""

from __future__ import annotations

import asyncio
import logging

from asyncio import PriorityQueue

from urllib.parse import urlparse


from config import (
    START_URLS,
    CONCURRENT_REQUESTS,
    MAX_DEPTH,
    MAX_TOTAL_PAGES,
    LOG_FILE,
    LOG_LEVEL,
)

from models import CrawlTask

from fetcher import Fetcher

from parser import parse_html

from extractor import enrich

from scoring import score_record

from writer import JsonlWriter

from robots import RobotsManager

from state import StateManager

from utils import (
    normalize_url,
    calculate_priority,
    should_skip_url,
    get_domain,
)



###############################################################################
# LOGGING
###############################################################################

logging.basicConfig(

    level=getattr(
        logging,
        LOG_LEVEL,
    ),

    format=(
        "%(asctime)s "
        "%(levelname)s "
        "%(message)s"
    ),

    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)


logger = logging.getLogger(__name__)



###############################################################################
# CRAWLER
###############################################################################


class PSACrawler:


    def __init__(self):

        self.queue = PriorityQueue()

        self.visited_count = 0

        self.writer = JsonlWriter()

        self.state = StateManager()

        self.robots = RobotsManager()

        self.seen = set()



    ###########################################################################
    # QUEUE
    ###########################################################################

    async def add_url(
        self,
        url: str,
        depth: int = 0,
    ):

        url = normalize_url(url)


        if url in self.seen:

            return


        if should_skip_url(url):

            return


        if depth > MAX_DEPTH:

            return


        priority = calculate_priority(
            url
        )


        self.seen.add(url)


        await self.queue.put(
            CrawlTask(
                url=url,
                depth=depth,
                priority=priority,
            )
        )



    ###########################################################################
    # WORKER
    ###########################################################################

    async def worker(
        self,
        fetcher: Fetcher,
    ):


        while True:


            task = await self.queue.get()


            try:


                if (
                    self.visited_count
                    >= MAX_TOTAL_PAGES
                ):

                    continue



                url = task.url


                ###############################################################
                # STATE CHECK
                ###############################################################

                if self.state.visited(url):

                    continue



                ###############################################################
                # ROBOTS
                ###############################################################

                allowed = await self.robots.allowed(
                    url,
                    fetcher.session,
                )


                if not allowed:

                    logger.info(
                        "Robots blocked %s",
                        url,
                    )

                    continue



                ###############################################################
                # FETCH
                ###############################################################

                result = await fetcher.fetch(
                    url
                )


                if result is None:

                    await self.state.mark_failure(
                        url
                    )

                    continue



                self.visited_count += 1



                ###############################################################
                # PARSE
                ###############################################################

                page = parse_html(
                    url,
                    result.html,
                )


                ###############################################################
                # EXTRACT + SCORE
                ###############################################################

                for heading in page.headings:


                    heading = enrich(
                        heading
                    )


                    heading = score_record(
                        heading
                    )


                    await self.writer.write(
                        heading
                    )



                ###############################################################
                # STATE
                ###############################################################

                await self.state.mark_success(
                    url,
                    result.status,
                )



                ###############################################################
                # DISCOVER LINKS
                ###############################################################

                domain = get_domain(url)


                for link in page.links:


                    if get_domain(link) != domain:

                        continue


                    await self.add_url(
                        link,
                        task.depth + 1,
                    )



                if self.visited_count % 100 == 0:

                    await self.state.save()


                    logger.info(
                        "Pages crawled: %s",
                        self.visited_count,
                    )


            except Exception as exc:


                logger.exception(
                    "Worker error: %s",
                    exc,
                )


            finally:

                self.queue.task_done()



    ###########################################################################
    # RUN
    ###########################################################################

    async def run(self):


        await self.state.load()


        await self.writer.start()



        for url in START_URLS:

            await self.add_url(
                url,
                0,
            )



        async with Fetcher() as fetcher:


            workers = [

                asyncio.create_task(
                    self.worker(fetcher)
                )

                for _ in range(
                    CONCURRENT_REQUESTS
                )

            ]


            await self.queue.join()



            for worker in workers:

                worker.cancel()



        await self.writer.stop()


        await self.state.save()



        logger.info(
            "Finished crawl. Pages=%s",
            self.visited_count,
        )



###############################################################################
# ENTRYPOINT
###############################################################################

if __name__ == "__main__":


    crawler = PSACrawler()


    asyncio.run(
        crawler.run()
    )
