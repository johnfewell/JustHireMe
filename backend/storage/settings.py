from __future__ import annotations

from storage.sqlite import SQLiteStore


class SettingsStore:
    """Typed settings accessor backed by SQLite.

    Concurrency model: delegates to SQLiteStore's connection-per-operation
    factory and closes each connection before returning.
    """

    def __init__(self, sqlite_store: SQLiteStore):
        self._sqlite = sqlite_store

    def all(self) -> dict[str, str]:
        conn = self._sqlite.connect()
        try:
            rows = conn.execute("SELECT key,val FROM settings").fetchall()
            return {row[0]: row[1] for row in rows}
        finally:
            conn.close()

    def save_many(self, values: dict[str, object]) -> None:
        conn = self._sqlite.connect()
        try:
            for key, value in values.items():
                conn.execute(
                    "INSERT OR REPLACE INTO settings(key,val) VALUES(?,?)",
                    (key, str(value)),
                )
            conn.commit()
        finally:
            conn.close()

    def text(self, key: str, default: str = "") -> str:
        conn = self._sqlite.connect()
        try:
            row = conn.execute(
                "SELECT val FROM settings WHERE key=?",
                (key,),
            ).fetchone()
            return row[0] if row else default
        finally:
            conn.close()

    def bool(self, key: str, default: bool = False) -> bool:
        value = self.text(key, "true" if default else "false").strip().lower()
        return value in {"1", "true", "yes", "on"}
