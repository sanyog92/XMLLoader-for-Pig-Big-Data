"""
APScheduler wrapper that drives the full pipeline on a fixed interval.

Jobs:
  crawl_and_produce  – discover content, edit, upload
  cleanup            – delete old local files after N days
"""

from __future__ import annotations

import signal
import sys

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config.settings import CRAWL_INTERVAL_MINUTES, TIMEZONE
from utils.logger import logger


class BotScheduler:
    def __init__(self, pipeline_fn, cleanup_fn=None):
        self.pipeline_fn = pipeline_fn
        self.cleanup_fn = cleanup_fn
        self._scheduler = BlockingScheduler(timezone=TIMEZONE)

    def start(self) -> None:
        self._scheduler.add_job(
            self.pipeline_fn,
            trigger=IntervalTrigger(minutes=CRAWL_INTERVAL_MINUTES),
            id="crawl_and_produce",
            name="Crawl → Edit → Upload",
            replace_existing=True,
            max_instances=1,
        )

        if self.cleanup_fn:
            self._scheduler.add_job(
                self.cleanup_fn,
                trigger=IntervalTrigger(hours=6),
                id="cleanup",
                name="Cleanup old files",
                replace_existing=True,
            )

        signal.signal(signal.SIGINT, self._shutdown)
        signal.signal(signal.SIGTERM, self._shutdown)

        logger.info(
            f"Scheduler started. Pipeline will run every {CRAWL_INTERVAL_MINUTES} minutes."
        )
        self._scheduler.start()

    def _shutdown(self, signum, frame) -> None:
        logger.info("Shutting down scheduler...")
        self._scheduler.shutdown(wait=False)
        sys.exit(0)
