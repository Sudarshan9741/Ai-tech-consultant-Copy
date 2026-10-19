import asyncio
import logging

import httpx
import pytest

from app.config import Settings
from app.crawler import PoliteCrawler
from app.scheduler import DailySyncScheduler


def test_sitemap_fetch_retries_transient_http_failure(monkeypatch):
    class FakeClient:
        attempts = 0

        async def __aenter__(self):
            return self

        async def __aexit__(self, *_args):
            return None

        async def get(self, _url):
            self.attempts += 1
            if self.attempts == 1:
                raise httpx.ReadTimeout("temporary outage")
            return httpx.Response(
                200,
                request=httpx.Request("GET", "https://example.test/sitemap.xml"),
                content=(
                    b'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                    b'<url><loc>https://support.brilliantdirectories.com/support/solutions/articles/1</loc>'
                    b'<lastmod>2026-10-19</lastmod></url></urlset>'
                ),
            )

    fake_client = FakeClient()
    monkeypatch.setattr("app.crawler.httpx.AsyncClient", lambda **_kwargs: fake_client)
    monkeypatch.setattr("app.crawler.asyncio.sleep", _no_wait)

    urls = asyncio.run(PoliteCrawler().fetch_sitemap_urls())

    assert fake_client.attempts == 2
    assert urls["https://support.brilliantdirectories.com/support/solutions/articles/1"] == "2026-10-19"


async def _no_wait(_seconds):
    return None


def test_scheduler_configuration_from_environment(monkeypatch):
    monkeypatch.setenv("TASK1_SCHEDULED_SYNC_ENABLED", "false")
    monkeypatch.setenv("TASK1_SCHEDULED_SYNC_INTERVAL_SECONDS", "123")

    config = Settings()

    assert config.scheduled_sync_enabled is False
    assert config.scheduled_sync_interval_seconds == 123
    with pytest.raises(ValueError):
        Settings(scheduled_sync_interval_seconds=0)


def test_scheduler_start_is_idempotent_and_runs_at_configured_interval():
    async def scenario():
        calls = 0
        called_twice = asyncio.Event()

        async def sync():
            nonlocal calls
            calls += 1
            if calls >= 2:
                called_twice.set()

        scheduler = DailySyncScheduler(sync, interval_seconds=0.01)
        scheduler.start()
        task = scheduler._task
        scheduler.start()
        assert scheduler._task is task
        await asyncio.wait_for(called_twice.wait(), timeout=1)
        await scheduler.stop()
        assert calls >= 2
        assert scheduler._task is None

    asyncio.run(scenario())


def test_scheduler_logs_sync_failure_and_keeps_running(caplog):
    async def scenario():
        calls = 0
        recovered = asyncio.Event()

        async def sync():
            nonlocal calls
            calls += 1
            if calls == 1:
                raise RuntimeError("simulated crawler failure")
            recovered.set()

        scheduler = DailySyncScheduler(sync, interval_seconds=0.01)
        with caplog.at_level(logging.ERROR, logger="sync_scheduler"):
            scheduler.start()
            await asyncio.wait_for(recovered.wait(), timeout=1)
            await scheduler.stop()

        assert calls >= 2
        assert "Scheduled Knowledge Brain synchronization failed" in caplog.text
        assert "simulated crawler failure" in caplog.text

    asyncio.run(scenario())


def test_scheduler_waits_for_active_sync_then_shuts_down_cleanly():
    async def scenario():
        entered_sync = asyncio.Event()
        finish_sync = asyncio.Event()

        async def sync():
            entered_sync.set()
            await finish_sync.wait()

        scheduler = DailySyncScheduler(sync, interval_seconds=86400)
        scheduler.start()
        await asyncio.wait_for(entered_sync.wait(), timeout=1)
        stopping = asyncio.create_task(scheduler.stop())
        await asyncio.sleep(0)
        assert not stopping.done()
        finish_sync.set()
        await asyncio.wait_for(stopping, timeout=1)
        assert scheduler._task is None

    asyncio.run(scenario())


def test_scheduled_and_manual_syncs_share_non_overlapping_crawler_lock(monkeypatch):
    async def scenario():
        active = 0
        maximum_active = 0

        async def fake_sync(max_articles, force_resync):
            nonlocal active, maximum_active
            active += 1
            maximum_active = max(maximum_active, active)
            await asyncio.sleep(0.01)
            active -= 1
            return {}

        test_crawler = PoliteCrawler()
        monkeypatch.setattr(test_crawler, "_sync_sitemap", fake_sync)
        await asyncio.gather(test_crawler.sync_sitemap(), test_crawler.sync_sitemap())
        assert maximum_active == 1

    asyncio.run(scenario())


def test_fastapi_lifespan_starts_and_stops_scheduler(monkeypatch):
    import app.main as main_module

    class FakeScheduler:
        started = False
        stopped = False

        def start(self):
            self.started = True

        async def stop(self):
            self.stopped = True

    async def scenario():
        fake = FakeScheduler()
        monkeypatch.setattr(main_module, "sync_scheduler", fake)
        monkeypatch.setattr(main_module.settings, "scheduled_sync_enabled", True)
        monkeypatch.setattr(main_module, "ensure_seed_data", lambda: None)

        async with main_module.app.router.lifespan_context(main_module.app):
            assert fake.started is True
            assert fake.stopped is False

        assert fake.stopped is True

    asyncio.run(scenario())
