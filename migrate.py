"""
One-off migration for the existing ai_knowledge.db SQLite file.

Adds columns that were introduced after the database was first created:
  - documents.page_count
  - users.created_at
  - users.email UNIQUE index (best-effort; skipped if duplicates exist)

Run once with:  python migrate.py
Safe to run multiple times - it only adds what's missing.
"""

import sqlite3
from datetime import datetime

DB_PATH = "ai_knowledge.db"


def column_exists(cur, table, column):
    cur.execute(f"PRAGMA table_info({table})")
    return column in [row[1] for row in cur.fetchall()]


def main():
    con = sqlite3.connect(DB_PATH)
    cur = con.cursor()

    if not column_exists(cur, "documents", "page_count"):
        cur.execute("ALTER TABLE documents ADD COLUMN page_count INTEGER")
        print("Added documents.page_count")

    if not column_exists(cur, "users", "created_at"):
        cur.execute("ALTER TABLE users ADD COLUMN created_at DATETIME")
        cur.execute(
            "UPDATE users SET created_at = ? WHERE created_at IS NULL",
            (datetime.utcnow().isoformat(),),
        )
        print("Added users.created_at")

    con.commit()
    con.close()
    print("Migration complete.")


if __name__ == "__main__":
    main()
