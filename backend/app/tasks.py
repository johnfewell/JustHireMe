from __future__ import annotations

import asyncio
import inspect
import uuid
from collections.abc import Awaitable, Callable
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CancellationToken:
    def __init__(self):
        self._event = asyncio.Event()

    def cancel(self) -> None:
        self._event.set()

    @property
    def cancelled(self) -> bool:
        return self._event.is_set()

    def throw_if_cancelled(self) -> None:
        if self.cancelled:
            raise asyncio.CancelledError()

    async def wait(self) -> None:
        await self._event.wait()


@dataclass
class TaskRecord:
    id: str
    name: str
    status: TaskStatus = TaskStatus.PENDING
    token: CancellationToken = field(default_factory=CancellationToken)
    result: Any = None
    error: str = ""


WorkFn = Callable[[CancellationToken], Any | Awaitable[Any]]


class TaskRegistry:
    """Async task registry with cancellable worker-pool execution."""

    def __init__(self, max_workers: int = 4):
        self._records: dict[str, TaskRecord] = {}
        self._tasks: dict[str, asyncio.Task] = {}
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = asyncio.Lock()

    async def submit(self, name: str, work: WorkFn) -> TaskRecord:
        record = TaskRecord(id=str(uuid.uuid4()), name=name)
        async with self._lock:
            self._records[record.id] = record
            self._tasks[record.id] = asyncio.create_task(self._run(record, work))
        return record

    async def _run(self, record: TaskRecord, work: WorkFn) -> None:
        record.status = TaskStatus.RUNNING
        try:
            record.token.throw_if_cancelled()
            if inspect.iscoroutinefunction(work):
                record.result = await work(record.token)
            else:
                value = await asyncio.get_running_loop().run_in_executor(
                    self._executor,
                    lambda: work(record.token),
                )
                if inspect.isawaitable(value):
                    record.result = await value
                else:
                    record.result = value
            record.token.throw_if_cancelled()
            record.status = TaskStatus.COMPLETED
        except asyncio.CancelledError:
            record.status = TaskStatus.CANCELLED
        except Exception as exc:
            record.status = TaskStatus.FAILED
            record.error = str(exc)

    def get(self, task_id: str) -> TaskRecord | None:
        return self._records.get(task_id)

    def list(self) -> list[TaskRecord]:
        return list(self._records.values())

    def cancel(self, task_id: str) -> bool:
        record = self._records.get(task_id)
        if record is None:
            return False
        record.token.cancel()
        if record.status in {TaskStatus.PENDING, TaskStatus.RUNNING}:
            record.status = TaskStatus.CANCELLED
        task = self._tasks.get(task_id)
        if task is not None:
            task.cancel()
        return True

    async def wait(self, task_id: str) -> TaskRecord | None:
        task = self._tasks.get(task_id)
        if task is not None:
            await asyncio.gather(task, return_exceptions=True)
        return self.get(task_id)

    async def shutdown(self) -> None:
        for record in self._records.values():
            record.token.cancel()
        for task in self._tasks.values():
            task.cancel()
        if self._tasks:
            await asyncio.gather(*self._tasks.values(), return_exceptions=True)
        self._executor.shutdown(wait=False, cancel_futures=True)
