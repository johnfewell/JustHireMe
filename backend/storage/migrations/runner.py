from __future__ import annotations

import importlib
import pkgutil
import sqlite3

MIGRATIONS_PACKAGE = "storage.migrations"


def _migration_modules() -> list[str]:
    package = importlib.import_module(MIGRATIONS_PACKAGE)
    return sorted(
        module.name
        for module in pkgutil.iter_modules(package.__path__)
        if module.name[:4].isdigit()
    )


def apply_migrations(conn: sqlite3.Connection) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS storage_migrations(
            version TEXT PRIMARY KEY,
            applied_at TEXT DEFAULT (datetime('now'))
        )
        """
    )
    applied = {
        row[0]
        for row in conn.execute("SELECT version FROM storage_migrations").fetchall()
    }
    for module_name in _migration_modules():
        if module_name in applied:
            continue
        module = importlib.import_module(f"{MIGRATIONS_PACKAGE}.{module_name}")
        module.apply(conn)
        conn.execute(
            "INSERT INTO storage_migrations(version) VALUES(?)",
            (module_name,),
        )
    conn.commit()
