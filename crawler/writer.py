"""
Asynchronous JSONL writer.

Responsibilities:
    - Stream records to disk
    - Deduplicate records
    - Batch writes
    - Avoid losing data during long crawls
"""

from __future__ import annotations

import asyncio
import json
import logging

from pathlib import Path

from typing import Optional

from models import HeadingRecord

from config import (
    JSONL_FILE,
)


logger = logging.getLogger(__name__)


class JsonlWriter:
    """
    Async-safe JSONL writer.

    One writer task consumes records from a queue.
    Multiple crawler workers can submit records.
    """

    def __init__(
        self,
        filepath: Path = JSONL_FILE,
        batch_size: int = 100,
    ):

        self.filepath = filepath

        self.batch_size = batch_size

        self.queue: asyncio.Queue = asyncio.Queue()

        self.task: Optional[asyncio.Task] = None

        self.running = False

        self.seen_hashes = set()


    ###########################################################################
    # START / STOP
    ###########################################################################

    async def start(self):

        self.running = True

        self.task = asyncio.create_task(
            self._writer_loop()
        )


    async def stop(self):

        self.running = False

        await self.queue.put(None)

        if self.task:

            await self.task


    ###########################################################################
    # ADD RECORD
    ###########################################################################

    async def write(
        self,
        record: HeadingRecord,
    ):
        """
        Add a record to the queue.
        """

        await self.queue.put(record)


    ###########################################################################
    # INTERNAL LOOP
    ###########################################################################

    async def _writer_loop(self):

        buffer = []


        self.filepath.parent.mkdir(
            parents=True,
            exist_ok=True,
        )


        with open(
            self.filepath,
            "a",
            encoding="utf-8",
        ) as f:


            while self.running:


                item = await self.queue.get()


                # shutdown signal
                if item is None:
                    break


                if not isinstance(
                    item,
                    HeadingRecord,
                ):

                    continue


                #################################################################
                # Deduplication
                #################################################################

                if item.hash:

                    if item.hash in self.seen_hashes:

                        logger.debug(
                            "Duplicate skipped: %s",
                            item.heading,
                        )

                        continue


                    self.seen_hashes.add(
                        item.hash
                    )


                #################################################################
                # Buffer
                #################################################################

                buffer.append(
                    json.dumps(
                        item.to_dict(),
                        ensure_ascii=False,
                    )
                )


                #################################################################
                # Flush batch
                #################################################################

                if len(buffer) >= self.batch_size:


                    f.write(
                        "\n".join(buffer)
                        + "\n"
                    )

                    f.flush()

                    buffer.clear()



            #####################################################################
            # Final flush
            #####################################################################

            if buffer:

                f.write(
                    "\n".join(buffer)
                    + "\n"
                )

                f.flush()
