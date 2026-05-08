import importlib
import sys


def _real_storage_classes():
    sys.modules.pop("sqlite3", None)
    sqlite3 = importlib.import_module("sqlite3")
    for module_name in ["storage.sqlite", "storage.settings"]:
        sys.modules.pop(module_name, None)
    sqlite_module = importlib.import_module("storage.sqlite")
    settings_module = importlib.import_module("storage.settings")
    return sqlite3, sqlite_module.SQLiteStore, settings_module.SettingsStore


def _real_graph_store():
    for module_name in ["kuzu", "storage.graph"]:
        sys.modules.pop(module_name, None)
    graph_module = importlib.import_module("storage.graph")
    return graph_module.GraphStore, graph_module


def test_sqlite_store_connects_lazily(tmp_path):
    _sqlite3, SQLiteStore, _SettingsStore = _real_storage_classes()
    calls = []
    db_path = tmp_path / "crm.db"

    store = SQLiteStore(str(db_path), lambda path: calls.append(path) or path)

    assert calls == []
    conn = store.connect()
    conn.close()

    assert calls == [str(tmp_path)]
    assert db_path.exists()


def test_settings_store_exposes_typed_accessors(tmp_path):
    _sqlite3, SQLiteStore, SettingsStore = _real_storage_classes()
    store = SQLiteStore(str(tmp_path / "crm.db"), lambda path: path)
    settings = SettingsStore(store)

    settings.save_many({"feature_enabled": "true", "candidate_name": "Ada"})

    assert settings.text("candidate_name") == "Ada"
    assert settings.bool("feature_enabled") is True
    assert settings.bool("missing") is False


def test_sqlite_store_is_compatible_with_sqlite_connection(tmp_path):
    sqlite3, SQLiteStore, _SettingsStore = _real_storage_classes()
    store = SQLiteStore(str(tmp_path / "crm.db"), lambda path: path)
    conn = store.connect()
    try:
        assert isinstance(conn, sqlite3.Connection)
    finally:
        conn.close()


def test_graph_store_ensures_parent_without_rewriting_existing_graph_file(tmp_path, monkeypatch):
    GraphStore, graph_module = _real_graph_store()
    calls = []
    graph_path = tmp_path / "graph"
    graph_path.write_text("existing kuzu database marker")

    class FakeKuzu:
        class Database:
            def __init__(self, path):
                self.path = path

        class Connection:
            def __init__(self, db):
                self.db = db

    monkeypatch.setattr(graph_module, "kuzu", FakeKuzu)
    store = GraphStore(str(graph_path), lambda path: calls.append(path) or path)

    db = store.database()

    assert calls == [str(tmp_path)]
    assert db.path == str(graph_path)
