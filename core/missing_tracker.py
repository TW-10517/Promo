"""
Local storage for "missing information" tracking.

Some fields required for the outputs — especially the Action Plan's owner,
deadline, cost, and price columns — can only come from the Planning
Department and are never present in the Planning Document itself. Rather
than making the user scan every generated file for blanks or
"[MISSING: ...]" markers, each generation run's missing items are recorded
here so the Promotion Department has a persistent, browsable follow-up list.

Storage is a small SQLite database under ``data/missing_items.db``. SQLite
(via the standard library, no extra dependency) is plenty for this scale — a
handful of runs a day, at most a few dozen items per run — and lets past
records be queried (e.g. "what was missing last time for Project X") without
loading everything into memory.
"""

from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from core import config

DB_FILENAME = "missing_items.db"

_SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_filename TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS missing_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id INTEGER NOT NULL REFERENCES runs(id) ON DELETE CASCADE,
    output TEXT NOT NULL,
    field TEXT NOT NULL,
    context TEXT,
    resolved INTEGER NOT NULL DEFAULT 0,
    resolved_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_missing_items_run_id ON missing_items(run_id);
CREATE INDEX IF NOT EXISTS idx_runs_source_filename ON runs(source_filename);
"""


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class MissingItem:
    """
    One missing piece of information for one generated output.

    Builders construct these with only ``field``/``context`` set (they don't
    know which output kind or run they belong to). The router fills in
    ``output`` before persisting; ``id``/``resolved``/``resolved_at`` are only
    meaningful once the item has round-tripped through the database.
    """

    field: str
    context: str | None = None
    output: str = ""
    id: int | None = None
    resolved: bool = False
    resolved_at: str | None = None


@dataclass
class RunRecord:
    """One generation run, identified by its source file and when it ran."""

    id: int
    source_filename: str
    timestamp: str  # ISO 8601
    created_at: str


# ---------------------------------------------------------------------------
# Connection / schema
# ---------------------------------------------------------------------------

def data_dir() -> Path:
    """Folder holding the local tracking database (created on first use)."""
    directory = config.app_dir() / "data"
    directory.mkdir(parents=True, exist_ok=True)
    return directory


def default_db_path() -> Path:
    return data_dir() / DB_FILENAME


@contextmanager
def _connect(target_db_path: Path | None = None):
    p = target_db_path or default_db_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(p))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db(db_path: Path | None = None) -> None:
    """Create the tables if they don't exist yet. Safe to call repeatedly."""
    with _connect(db_path) as conn:
        conn.executescript(_SCHEMA)


# ---------------------------------------------------------------------------
# Writing
# ---------------------------------------------------------------------------

def create_run(
    source_filename: str,
    timestamp: datetime | None = None,
    db_path: Path | None = None,
) -> int:
    """Create a run record and return its id."""
    init_db(db_path)
    ts = (timestamp or datetime.now()).isoformat(timespec="seconds")
    now = datetime.now().isoformat(timespec="seconds")
    with _connect(db_path) as conn:
        cursor = conn.execute(
            "INSERT INTO runs (source_filename, timestamp, created_at) VALUES (?, ?, ?)",
            (source_filename, ts, now),
        )
        return cursor.lastrowid


def add_missing_items(
    run_id: int,
    items: list[MissingItem],
    db_path: Path | None = None,
) -> None:
    """
    Persist the missing items detected for one run. No-op for an empty list.

    Writes each row's real DB id back onto the MissingItem object passed in
    (executemany can't return per-row ids, so this inserts one at a time) so
    callers can resolve these exact objects later via ``resolve_item``.
    """
    if not items:
        return
    init_db(db_path)
    with _connect(db_path) as conn:
        for item in items:
            cursor = conn.execute(
                "INSERT INTO missing_items (run_id, output, field, context) VALUES (?, ?, ?, ?)",
                (run_id, item.output, item.field, item.context),
            )
            item.id = cursor.lastrowid


def mark_resolved(
    item_id: int,
    resolved: bool = True,
    db_path: Path | None = None,
) -> None:
    """Toggle one item's resolved flag (called when the user ticks it off in the UI)."""
    init_db(db_path)
    resolved_at = datetime.now().isoformat(timespec="seconds") if resolved else None
    with _connect(db_path) as conn:
        conn.execute(
            "UPDATE missing_items SET resolved = ?, resolved_at = ? WHERE id = ?",
            (1 if resolved else 0, resolved_at, item_id),
        )


# ---------------------------------------------------------------------------
# Reading
# ---------------------------------------------------------------------------

def _row_to_item(row: sqlite3.Row) -> MissingItem:
    return MissingItem(
        id=row["id"],
        output=row["output"],
        field=row["field"],
        context=row["context"],
        resolved=bool(row["resolved"]),
        resolved_at=row["resolved_at"],
    )


def _row_to_run(row: sqlite3.Row) -> RunRecord:
    return RunRecord(
        id=row["id"],
        source_filename=row["source_filename"],
        timestamp=row["timestamp"],
        created_at=row["created_at"],
    )


def get_missing_items(run_id: int, db_path: Path | None = None) -> list[MissingItem]:
    """All missing items for one run, in a stable order (grouped by output)."""
    init_db(db_path)
    with _connect(db_path) as conn:
        rows = conn.execute(
            "SELECT * FROM missing_items WHERE run_id = ? ORDER BY output, id",
            (run_id,),
        ).fetchall()
    return [_row_to_item(row) for row in rows]


def list_runs(
    source_filename: str | None = None,
    limit: int = 200,
    db_path: Path | None = None,
) -> list[RunRecord]:
    """List past runs, newest first. Optionally filtered by exact source filename."""
    init_db(db_path)
    with _connect(db_path) as conn:
        if source_filename:
            rows = conn.execute(
                "SELECT * FROM runs WHERE source_filename = ? ORDER BY id DESC LIMIT ?",
                (source_filename, limit),
            )
        else:
            rows = conn.execute(
                "SELECT * FROM runs ORDER BY id DESC LIMIT ?", (limit,)
            )
        rows = rows.fetchall()
    return [_row_to_run(row) for row in rows]


def get_run(run_id: int, db_path: Path | None = None) -> RunRecord | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute("SELECT * FROM runs WHERE id = ?", (run_id,)).fetchone()
    return _row_to_run(row) if row is not None else None


def latest_run_for_source(
    source_filename: str,
    db_path: Path | None = None,
) -> RunRecord | None:
    """
    Most recent run for a given Planning Document filename.
    """
    runs = list_runs(source_filename=source_filename, limit=1, db_path=db_path)
    return runs[0] if runs else None


def pending_count(run_id: int, db_path: Path | None = None) -> int:
    """How many of a run's missing items are still unresolved."""
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM missing_items WHERE run_id = ? AND resolved = 0",
            (run_id,),
        ).fetchone()
    return row["c"] if row else 0


# ---------------------------------------------------------------------------
# UI-facing convenience wrappers
# ---------------------------------------------------------------------------
#
# get_missing_items() needs a specific run_id and returns MissingItem
# dataclasses; UI code that just wants "everything across every run, as
# plain dicts" (e.g. a single flat checklist table) uses these instead so it
# doesn't have to join runs + items itself.

def list_missing_items(db_path: Path | None = None) -> list[dict]:
    """
    Every missing item across every run, newest run first, as plain dicts.

    Each dict has: id, resolved, field_name, context, first_seen, resolved_at.
    ``context`` folds in the output name (e.g. "実施計画書 (Action Plan)")
    since a single flat table has no separate column for it.
    """
    out: list[dict] = []
    for run in list_runs(db_path=db_path):
        for item in get_missing_items(run.id, db_path=db_path):
            context = f"{item.output} — {item.context}" if item.context else item.output
            out.append(
                {
                    "id": item.id,
                    "resolved": item.resolved,
                    "field_name": item.field,
                    "context": context,
                    "first_seen": run.timestamp,
                    "resolved_at": item.resolved_at,
                }
            )
    return out


def resolve_item(item_id: int, resolved: bool = True, db_path: Path | None = None) -> None:
    """Alias for ``mark_resolved`` under the name the UI checklist expects."""
    mark_resolved(item_id, resolved=resolved, db_path=db_path)
