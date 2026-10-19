import asyncio
import logging
from typing import Awaitable, Callable, Optional

logger = logging.getLogger("sync_scheduler")
SyncFunction = Callable[[], Awaitable[object]]


class DailySyncScheduler:
    """Run one incremental sync immediately, then after each configured interval."""

    def __init__(self, sync: SyncFunction, interval_seconds: float):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be greater than zero")
        self._sync = sync
        self.interval_seconds = interval_seconds
        self._task: Optional[asyncio.Task] = None
        self._stop_event: Optional[asyncio.Event] = None

    def start(self) -> None:
        if self._task is not None and not self._task.done():
            return
        self._stop_event = asyncio.Event()
        self._task = asyncio.create_task(self._run(), name="task1-daily-sync")

    async def stop(self) -> None:
        task = self._task
        if task is None:
            return
        if self._stop_event is not None:
            self._stop_event.set()
        await task
        self._task = None
        self._stop_event = None

    async def _run(self) -> None:
        stop_event = self._stop_event
        assert stop_event is not None
        while True:
            try:
                await self._sync()
            except Exception:
                logger.exception("Scheduled Knowledge Brain synchronization failed")

            try:
                await asyncio.wait_for(stop_event.wait(), timeout=self.interval_seconds)
                return
            except asyncio.TimeoutError:
                continue

