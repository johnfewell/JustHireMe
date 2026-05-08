from __future__ import annotations

import os
import sqlite3
import threading
from collections.abc import Callable

from storage.migrations.runner import apply_migrations


class SQLiteStore:
    """SQLite connection factory.

    Concurrency model: one short-lived connection per operation. Migration
    startup is protected by a process-local lock so concurrent first use does
    not race schema creation.
    """

    def __init__(self, path: str, ensure_dir: Callable[[str], str]):
        self.path = path
        self._ensure_dir = ensure_dir
        self._initialized = False
        self._lock = threading.Lock()

    def connect(self) -> sqlite3.Connection:
        if not self._initialized:
            with self._lock:
                if not self._initialized:
                    self._ensure_dir(os.path.dirname(self.path))
                    conn = sqlite3.connect(self.path)
                    try:
                        apply_migrations(conn)
                    finally:
                        conn.close()
                    self._initialized = True
        return sqlite3.connect(self.path)
