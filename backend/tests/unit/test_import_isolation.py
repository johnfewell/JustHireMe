import importlib
import sys
import types


def test_storage_modules_do_not_open_storage_on_import(monkeypatch):
    calls = []

    def fail(name):
        def _inner(*_args, **_kwargs):
            calls.append(name)
            raise AssertionError(f"{name} should not run at import time")

        return _inner

    monkeypatch.setattr("os.makedirs", fail("os.makedirs"))

    fake_sqlite = types.SimpleNamespace(
        connect=fail("sqlite3.connect"),
        Row=object,
    )
    fake_kuzu = types.SimpleNamespace(
        Database=fail("kuzu.Database"),
        Connection=fail("kuzu.Connection"),
    )
    fake_lancedb = types.SimpleNamespace(
        connect=fail("lancedb.connect"),
        LanceDBConnection=object,
    )
    monkeypatch.setitem(sys.modules, "sqlite3", fake_sqlite)
    monkeypatch.setitem(sys.modules, "kuzu", fake_kuzu)
    monkeypatch.setitem(sys.modules, "lancedb", fake_lancedb)

    module_names = [
        "db.client",
        "agents.generator",
        "agents.ingestor",
    ]
    try:
        for module_name in module_names:
            sys.modules.pop(module_name, None)
            importlib.import_module(module_name)
    finally:
        for module_name in module_names:
            sys.modules.pop(module_name, None)

    assert calls == []
