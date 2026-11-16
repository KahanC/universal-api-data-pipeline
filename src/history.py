import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_DB = Path("outputs/pipeline_history.db")


def initialize_database(db_path=DEFAULT_DB):
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS profile_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pipeline_name TEXT NOT NULL,
                run_timestamp TEXT NOT NULL,
                row_count INTEGER NOT NULL,
                column_count INTEGER NOT NULL,
                completeness_pct REAL NOT NULL,
                duplicate_rows INTEGER NOT NULL,
                profile_json TEXT NOT NULL
            )
        """)

        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_pipeline_history
            ON profile_snapshots(pipeline_name, id)
        """)


def save_snapshot(pipeline_name, profile, db_path=DEFAULT_DB):
    """Persist the profile of a successfully validated run."""
    initialize_database(db_path)

    overview = profile["overview"]
    timestamp = datetime.now(timezone.utc).isoformat()

    # Store detailed column-level metrics as JSON.
    payload = {
        "overview": overview,
        "columns": profile["columns"].to_dict(orient="records"),
        "numeric": profile["numeric"].to_dict(orient="records"),
        "categories": profile["categories"].to_dict(orient="records"),
    }

    with sqlite3.connect(db_path) as conn:
        cursor = conn.execute("""
            INSERT INTO profile_snapshots (
                pipeline_name,
                run_timestamp,
                row_count,
                column_count,
                completeness_pct,
                duplicate_rows,
                profile_json
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            pipeline_name,
            timestamp,
            overview["rows"],
            overview["columns"],
            overview["completeness_pct"],
            overview["duplicate_rows"],
            json.dumps(payload, default=str),
        ))

        snapshot_id = cursor.lastrowid

    return snapshot_id


def get_latest_snapshots(
    pipeline_name, limit=2, db_path=DEFAULT_DB
):
    """Retrieve recent snapshots, newest first."""
    initialize_database(db_path)

    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row

        rows = conn.execute("""
            SELECT *
            FROM profile_snapshots
            WHERE pipeline_name = ?
            ORDER BY id DESC
            LIMIT ?
        """, (pipeline_name, limit)).fetchall()

    snapshots = []

    for row in rows:
        record = dict(row)
        record["profile"] = json.loads(
            record.pop("profile_json")
        )
        snapshots.append(record)

    return snapshots
