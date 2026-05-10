"""
Desktop AI Lifeform — Persistent Memory (memory.py)
====================================================
SQLite-backed memory for the creature. Stores emotional variables,
event history, app habits, and ambient phrase history.

Everything here is intentionally simple. The creature remembers,
but not perfectly — just like real memory.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from backend import config

logger = logging.getLogger(__name__)


# ── Schema ─────────────────────────────────────────────────────────────────────

SCHEMA = """
-- Persistent emotional variables, updated on shutdown/interval
CREATE TABLE IF NOT EXISTS creature_state (
    key   TEXT PRIMARY KEY,
    value REAL NOT NULL,
    updated_at TEXT NOT NULL
);

-- Log of significant events (builds, sessions, crashes, etc.)
CREATE TABLE IF NOT EXISTS event_log (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    event      TEXT NOT NULL,
    intensity  REAL DEFAULT 1.0,
    context    TEXT,          -- JSON blob with extra context
    occurred_at TEXT NOT NULL
);

-- Per-app usage tracking (for habits / favorites)
CREATE TABLE IF NOT EXISTS app_habits (
    app_class  TEXT NOT NULL,
    app_name   TEXT NOT NULL,
    session_count  INTEGER DEFAULT 0,
    total_minutes  REAL    DEFAULT 0.0,
    last_seen  TEXT,
    PRIMARY KEY (app_class, app_name)
);

-- Short ambient phrases remembered to avoid repetition
CREATE TABLE IF NOT EXISTS phrase_history (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase     TEXT NOT NULL,
    state      TEXT,
    said_at    TEXT NOT NULL
);

-- Metadata / misc key-value store
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);
"""


# ── Memory class ───────────────────────────────────────────────────────────────

class Memory:
    def __init__(self, db_path: str = config.DB_PATH):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.db_path = db_path
        self._conn: Optional[sqlite3.Connection] = None
        self._connect()
        self._init_schema()
        self._ensure_meta()
        logger.info(f"Memory initialised at {db_path}")

    def _connect(self):
        self._conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA journal_mode=WAL")

    def _init_schema(self):
        self._conn.executescript(SCHEMA)
        self._conn.commit()

    def _ensure_meta(self):
        """Set first_boot timestamp if not already set."""
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key='first_boot'"
        ).fetchone()
        if not row:
            self._conn.execute(
                "INSERT INTO meta(key,value) VALUES(?,?)",
                ("first_boot", datetime.utcnow().isoformat())
            )
            self._conn.commit()

    # ── Emotional variables ────────────────────────────────────────────────────

    def load_vars(self) -> Dict[str, float]:
        """Load all persisted emotional variables."""
        rows = self._conn.execute(
            "SELECT key, value FROM creature_state"
        ).fetchall()
        return {r["key"]: r["value"] for r in rows}

    def save_vars(self, vars_dict: Dict[str, float]):
        """Persist current emotional variables."""
        now = datetime.utcnow().isoformat()
        for key, value in vars_dict.items():
            self._conn.execute(
                """INSERT INTO creature_state(key, value, updated_at)
                   VALUES(?,?,?)
                   ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at""",
                (key, float(value), now)
            )
        self._conn.commit()

    # ── Events ────────────────────────────────────────────────────────────────

    def log_event(self, event: str, intensity: float = 1.0, context: Optional[Dict] = None):
        """Record a significant event in the event log."""
        self._conn.execute(
            "INSERT INTO event_log(event, intensity, context, occurred_at) VALUES(?,?,?,?)",
            (event, intensity, json.dumps(context) if context else None,
             datetime.utcnow().isoformat())
        )
        self._conn.commit()

    def recent_events(self, limit: int = 20) -> List[Dict]:
        rows = self._conn.execute(
            "SELECT * FROM event_log ORDER BY occurred_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── App habits ────────────────────────────────────────────────────────────

    def record_app_session(self, app_class: str, app_name: str, minutes: float):
        """Track usage of a specific application."""
        now = datetime.utcnow().isoformat()
        self._conn.execute(
            """INSERT INTO app_habits(app_class, app_name, session_count, total_minutes, last_seen)
               VALUES(?,?,1,?,?)
               ON CONFLICT(app_class, app_name) DO UPDATE SET
                   session_count = session_count + 1,
                   total_minutes = total_minutes + excluded.total_minutes,
                   last_seen = excluded.last_seen""",
            (app_class, app_name, minutes, now)
        )
        self._conn.commit()

    def favorite_apps(self, limit: int = 5) -> List[Dict]:
        rows = self._conn.execute(
            """SELECT app_class, app_name, session_count, total_minutes
               FROM app_habits ORDER BY total_minutes DESC LIMIT ?""",
            (limit,)
        ).fetchall()
        return [dict(r) for r in rows]

    # ── Phrase history ────────────────────────────────────────────────────────

    def remember_phrase(self, phrase: str, state: str):
        self._conn.execute(
            "INSERT INTO phrase_history(phrase, state, said_at) VALUES(?,?,?)",
            (phrase, state, datetime.utcnow().isoformat())
        )
        self._conn.commit()

    def recent_phrases(self, limit: int = 10) -> List[str]:
        rows = self._conn.execute(
            "SELECT phrase FROM phrase_history ORDER BY said_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [r["phrase"] for r in rows]

    # ── Meta ──────────────────────────────────────────────────────────────────

    def get_meta(self, key: str) -> Optional[str]:
        row = self._conn.execute(
            "SELECT value FROM meta WHERE key=?", (key,)
        ).fetchone()
        return row["value"] if row else None

    def set_meta(self, key: str, value: str):
        self._conn.execute(
            "INSERT INTO meta(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
            (key, value)
        )
        self._conn.commit()

    def days_alive(self) -> int:
        """How many days since first boot."""
        first = self.get_meta("first_boot")
        if not first:
            return 0
        delta = datetime.utcnow() - datetime.fromisoformat(first)
        return delta.days

    def close(self):
        if self._conn:
            self._conn.close()
