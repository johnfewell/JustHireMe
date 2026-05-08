import sqlite3

from storage.settings import SettingsStore
from storage.sqlite import SQLiteStore


def test_sqlite_store_connects_lazily(tmp_path):
    calls = []
    db_path = tmp_path / "crm.db"

    store = SQLiteStore(str(db_path), lambda path: calls.append(path) or path)

    assert calls == []
    conn = store.connect()
    conn.close()

    assert calls == [str(tmp_path)]
    assert db_path.exists()


def test_settings_store_exposes_typed_accessors(tmp_path):
    store = SQLiteStore(str(tmp_path / "crm.db"), lambda path: path)
    settings = SettingsStore(store)

    settings.save_many({"feature_enabled": "true", "candidate_name": "Ada"})

    assert settings.text("candidate_name") == "Ada"
    assert settings.bool("feature_enabled") is True
    assert settings.bool("missing") is False


def test_sqlite_store_is_compatible_with_sqlite_connection(tmp_path):
    store = SQLiteStore(str(tmp_path / "crm.db"), lambda path: path)
    conn = store.connect()
    try:
        assert isinstance(conn, sqlite3.Connection)
    finally:
        conn.close()
