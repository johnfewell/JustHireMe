from __future__ import annotations

import threading
from collections.abc import Callable

import lancedb


class NullVectorStore:
    """No-op vector store so profile CRUD never fails when embeddings are unavailable."""

    def list_tables(self):
        return []

    def create_table(self, *_args, **_kwargs):
        return None

    def open_table(self, *_args, **_kwargs):
        return self

    def add(self, *_args, **_kwargs):
        return None


class VectorStore:
    """Lazy LanceDB connection holder.

    Concurrency model: a single LanceDB connection is initialized under a
    process-local lock and reused by callers.
    """

    def __init__(self, path: str, ensure_dir: Callable[[str], str]):
        self.path = path
        self._ensure_dir = ensure_dir
        self._store = None
        self._lock = threading.Lock()

    def store(self):
        if self._store is not None:
            return self._store
        with self._lock:
            if self._store is not None:
                return self._store
            try:
                self._store = lancedb.connect(self._ensure_dir(self.path))
            except Exception:
                self._store = NullVectorStore()
        return self._store
