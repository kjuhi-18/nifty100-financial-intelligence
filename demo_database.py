import sqlite3

conn = sqlite3.connect("db/nifty100.db")

tables = conn.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""").fetchall()

print("\nTABLES\n")

for table in tables:
    print(table[0])

print("\nFK CHECK")

print(
    conn.execute(
        "PRAGMA foreign_key_check"
    ).fetchall()
)

conn.close()