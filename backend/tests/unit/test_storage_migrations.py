import sqlite3

from storage.migrations.runner import apply_migrations


def test_apply_migrations_creates_schema_once():
    conn = sqlite3.connect(":memory:")

    apply_migrations(conn)
    apply_migrations(conn)

    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    }
    assert {"leads", "events", "settings", "storage_migrations"} <= tables

    columns = {
        row[1]
        for row in conn.execute("PRAGMA table_info(leads)").fetchall()
    }
    assert {"job_id", "kind", "signal_score", "resume_version"} <= columns

    versions = conn.execute(
        "SELECT version FROM storage_migrations ORDER BY version"
    ).fetchall()
    assert versions == [("0001_initial_sqlite",)]
