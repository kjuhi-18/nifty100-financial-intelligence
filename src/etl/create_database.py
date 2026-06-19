"""
Day 04 - SQLite Database Creation

Creates:
    db/nifty100.db

Uses:
    db/schema.sql

Verifies:
    - Tables created successfully
    - Foreign keys enabled
"""

import sqlite3
from pathlib import Path


# =====================================================
# PATHS
# =====================================================

PROJECT_ROOT = Path(__file__).resolve().parents[2]

DB_PATH = PROJECT_ROOT / "db" / "nifty100.db"
SCHEMA_PATH = PROJECT_ROOT / "db" / "schema.sql"


# =====================================================
# CREATE DATABASE
# =====================================================

def create_database():
    """
    Create SQLite database from schema.sql
    """

    print("\nCreating database...")

    # Create connection
    conn = sqlite3.connect(DB_PATH)

    # Enable foreign keys
    conn.execute("PRAGMA foreign_keys = ON;")

    # Read schema file
    with open(
        SCHEMA_PATH,
        "r",
        encoding="utf-8"
    ) as f:

        schema = f.read()

    # Execute schema
    conn.executescript(schema)

    conn.commit()

    print("Database created successfully.")

    return conn


# =====================================================
# VERIFY DATABASE
# =====================================================

def verify_database(conn):
    """
    Verify all tables exist
    """

    print("\nVerifying database...\n")

    cursor = conn.cursor()

    cursor.execute("""
        SELECT name
        FROM sqlite_master
        WHERE type='table'
        ORDER BY name
    """)

    tables = cursor.fetchall()

    print(f"Total Tables Created: {len(tables)}\n")

    for table in tables:
        print(f"{table[0]}")

    # Verify foreign keys
    fk_status = conn.execute(
        "PRAGMA foreign_keys;"
    ).fetchone()[0]

    print("\nForeign Keys Enabled:", bool(fk_status))


# =====================================================
# MAIN
# =====================================================

def main():

    conn = create_database()

    verify_database(conn)

    conn.close()

    


if __name__ == "__main__":
    main()