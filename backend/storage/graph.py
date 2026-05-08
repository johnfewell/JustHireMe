from __future__ import annotations

import threading
from collections.abc import Callable

import kuzu


class GraphStore:
    """Lazy Kuzu database holder.

    Concurrency model: a shared database handle is initialized under a lock;
    callers request fresh connections for operations that need isolation.
    """

    def __init__(self, path: str, ensure_dir: Callable[[str], str]):
        self.path = path
        self._ensure_dir = ensure_dir
        self._db = None
        self._conn = None
        self.error = ""
        self._lock = threading.Lock()

    def database(self):
        if self._db is not None:
            return self._db
        with self._lock:
            if self._db is not None:
                return self._db
            graph_path = self._ensure_dir(self.path)
            try:
                self._db = kuzu.Database(graph_path)
                self._conn = kuzu.Connection(self._db)
            except Exception as exc:
                self._db = None
                self._conn = None
                self.error = str(exc)
        return self._db

    def shared_connection(self):
        if self._conn is None:
            self.database()
        return self._conn

    def connection(self):
        db = self.database()
        if db is None:
            return None
        return kuzu.Connection(db)
