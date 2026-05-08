import importlib
import sys
import types
from pathlib import Path


BACKEND_ROOT = Path(__file__).resolve().parents[2]
IMPORT_EXCLUDES = {
    "force_model",
    "run_diagnostics",
    "test_ingestion",
    "test_live_fire",
    "update_settings",
}


def _backend_modules() -> list[str]:
    modules = []
    for path in sorted(BACKEND_ROOT.rglob("*.py")):
        if any(part in {".venv", "tests"} for part in path.parts):
            continue
        relative = path.relative_to(BACKEND_ROOT)
        if relative.name == "__init__.py":
            module_name = ".".join(relative.parts[:-1])
        else:
            module_name = ".".join(relative.with_suffix("").parts)
        if not module_name or module_name in IMPORT_EXCLUDES:
            continue
        modules.append(module_name)
    return modules


def test_backend_modules_do_not_open_storage_on_import(monkeypatch):
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

    module_names = _backend_modules()
    try:
        for module_name in module_names:
            sys.modules.pop(module_name, None)
            importlib.import_module(module_name)
    finally:
        for module_name in module_names:
            sys.modules.pop(module_name, None)

    assert calls == []
