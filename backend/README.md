# JustHireMe Backend

Python backend sidecar for JustHireMe.

## Responsibilities

- FastAPI HTTP/WebSocket API
- local CRM persistence
- source scraping
- lead quality gating
- deterministic and semantic ranking
- profile graph/vector ingestion
- resume, cover letter, and outreach generation

## Setup

From the repository root:

```bash
cd backend
uv sync --dev
```

## Tests

Windows:

```bash
backend/.venv/Scripts/python.exe -m pytest backend/tests
```

macOS/Linux:

```bash
backend/.venv/bin/python -m pytest backend/tests
```

## Migration Shims

Temporary compatibility shims for storage or IPC migrations must include the exact marker `# TODO(migration): remove in phase 5`. Keep the marker on the shim itself or the smallest enclosing block so cleanup can be verified with:

```bash
rg "# TODO\\(migration\\): remove in phase 5" backend
```

## Storage Migrations

SQLite schema changes live in `storage/migrations/` as versioned Python modules named with a zero-padded numeric prefix, for example `0002_add_example.py`. Each migration exposes `apply(conn)` and is applied once by `storage.migrations.runner.apply_migrations` on first SQLite connection.

Migration files run in lexical order. To add a migration, create the next numbered file, keep it idempotent for partially upgraded local databases, and avoid importing app modules from migrations.

## Notes

The backend stores local user data through SQLite, Kuzu, LanceDB, and generated files. Do not commit local app data, vector stores, graph databases, generated PDFs, API keys, cookies, or private resumes.
