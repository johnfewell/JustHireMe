import asyncio

import pytest

from app.tasks import TaskRegistry, TaskStatus


@pytest.mark.anyio
async def test_task_registry_runs_sync_work():
    registry = TaskRegistry(max_workers=1)
    try:
        record = await registry.submit("sync", lambda token: "done")
        finished = await registry.wait(record.id)

        assert finished is not None
        assert finished.status == TaskStatus.COMPLETED
        assert finished.result == "done"
    finally:
        await registry.shutdown()


@pytest.mark.anyio
async def test_task_registry_runs_async_work():
    registry = TaskRegistry(max_workers=1)

    async def work(token):
        await asyncio.sleep(0)
        token.throw_if_cancelled()
        return 42

    try:
        record = await registry.submit("async", work)
        finished = await registry.wait(record.id)

        assert finished is not None
        assert finished.status == TaskStatus.COMPLETED
        assert finished.result == 42
    finally:
        await registry.shutdown()


@pytest.mark.anyio
async def test_task_registry_cancels_running_work():
    registry = TaskRegistry(max_workers=1)

    async def work(token):
        await token.wait()
        token.throw_if_cancelled()

    try:
        record = await registry.submit("cancel", work)
        assert registry.cancel(record.id) is True
        finished = await registry.wait(record.id)

        assert finished is not None
        assert finished.status == TaskStatus.CANCELLED
        assert finished.token.cancelled is True
    finally:
        await registry.shutdown()
