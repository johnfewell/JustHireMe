from __future__ import annotations


def get_events(limit: int = 100, job_id: str | None = None) -> list[dict]:
    from db.client import get_events as _get_events

    return _get_events(limit=limit, job_id=job_id)
