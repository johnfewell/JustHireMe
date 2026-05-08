LEAD_COLUMNS = [
    ("score", "INTEGER DEFAULT 0"),
    ("reason", "TEXT DEFAULT ''"),
    ("match_points", "TEXT DEFAULT ''"),
    ("asset_path", "TEXT DEFAULT ''"),
    ("cover_letter_path", "TEXT DEFAULT ''"),
    ("selected_projects", "TEXT DEFAULT ''"),
    ("description", "TEXT DEFAULT ''"),
    ("gaps", "TEXT DEFAULT ''"),
    ("kind", "TEXT DEFAULT 'job'"),
    ("budget", "TEXT DEFAULT ''"),
    ("signal_score", "INTEGER DEFAULT 0"),
    ("signal_reason", "TEXT DEFAULT ''"),
    ("signal_tags", "TEXT DEFAULT ''"),
    ("outreach_reply", "TEXT DEFAULT ''"),
    ("outreach_dm", "TEXT DEFAULT ''"),
    ("source_meta", "TEXT DEFAULT ''"),
    ("feedback", "TEXT DEFAULT ''"),
    ("feedback_note", "TEXT DEFAULT ''"),
    ("followup_due_at", "TEXT DEFAULT ''"),
    ("last_contacted_at", "TEXT DEFAULT ''"),
    ("outreach_email", "TEXT DEFAULT ''"),
    ("proposal_draft", "TEXT DEFAULT ''"),
    ("fit_bullets", "TEXT DEFAULT ''"),
    ("followup_sequence", "TEXT DEFAULT ''"),
    ("proof_snippet", "TEXT DEFAULT ''"),
    ("tech_stack", "TEXT DEFAULT ''"),
    ("location", "TEXT DEFAULT ''"),
    ("urgency", "TEXT DEFAULT ''"),
    ("base_signal_score", "INTEGER DEFAULT 0"),
    ("learning_delta", "INTEGER DEFAULT 0"),
    ("learning_reason", "TEXT DEFAULT ''"),
    ("resume_version", "INTEGER DEFAULT 0"),
]


def apply(conn):
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS leads(
            job_id TEXT PRIMARY KEY, title TEXT, company TEXT,
            url TEXT, platform TEXT, status TEXT DEFAULT 'discovered',
            score INTEGER DEFAULT 0,
            reason TEXT DEFAULT '',
            match_points TEXT DEFAULT '',
            asset_path TEXT DEFAULT '',
            cover_letter_path TEXT DEFAULT '',
            selected_projects TEXT DEFAULT '',
            description TEXT DEFAULT '',
            gaps TEXT DEFAULT '',
            resume_version INTEGER DEFAULT 0,
            created_at TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS events(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_id TEXT, action TEXT, ts TEXT DEFAULT (datetime('now'))
        );
        CREATE TABLE IF NOT EXISTS settings(
            key TEXT PRIMARY KEY, val TEXT
        );
        """
    )
    existing = {
        row[1]
        for row in conn.execute("PRAGMA table_info(leads)").fetchall()
    }
    for column, definition in LEAD_COLUMNS:
        if column not in existing:
            conn.execute(f"ALTER TABLE leads ADD COLUMN {column} {definition}")
