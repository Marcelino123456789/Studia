"""
One-time migration script: copies existing data from the local SQLite
database (Studia.db) into the MySQL database used for deployment.

Usage:
    1. Create the MySQL database and run schema.sql against it first.
    2. Set the same DB_HOST / DB_PORT / DB_USER / DB_PASSWORD / DB_NAME
       environment variables used by app.py (e.g. `source` a .env file,
       or export them in your shell).
    3. Run:  python migrate_sqlite_to_mysql.py
       (optionally pass the sqlite path as an argument, default Studia.db)

The script preserves existing primary key IDs (so foreign keys such as
notes.user_id, messages.sender_id/receiver_id, etc. keep pointing at the
right rows), and copies tables in an order that respects the notes ->
users foreign key. It is safe to run on an empty SQLite database -- it
will simply copy nothing.

If Studia.db has no rows in any table, this script is not needed; you
can start with an empty MySQL database created from schema.sql alone.
"""

import os
import sys
import sqlite3

import pymysql


TABLES_IN_ORDER = ["users", "notes", "tasks", "messages", "friends", "timers"]


def get_mysql_connection():
    required = ["DB_HOST", "DB_USER", "DB_PASSWORD", "DB_NAME"]
    missing = [name for name in required if not os.environ.get(name)]
    if missing:
        sys.exit(
            "Missing required environment variables: " + ", ".join(missing)
        )

    return pymysql.connect(
        host=os.environ["DB_HOST"],
        port=int(os.environ.get("DB_PORT", "3306")),
        user=os.environ["DB_USER"],
        password=os.environ["DB_PASSWORD"],
        database=os.environ["DB_NAME"],
        autocommit=False,
    )


def migrate_table(sqlite_conn, mysql_conn, table):
    sqlite_cur = sqlite_conn.execute(f"SELECT * FROM {table}")
    rows = sqlite_cur.fetchall()
    if not rows:
        print(f"  {table}: no rows to migrate")
        return

    columns = rows[0].keys()
    placeholders = ", ".join(["%s"] * len(columns))
    column_list = ", ".join(f"`{c}`" for c in columns)
    insert_sql = f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})"

    with mysql_conn.cursor() as cur:
        for row in rows:
            cur.execute(insert_sql, tuple(row[c] for c in columns))

        # Keep future AUTO_INCREMENT ids from colliding with migrated ids.
        if "id" in columns:
            max_id = max(row["id"] for row in rows)
            cur.execute(f"ALTER TABLE {table} AUTO_INCREMENT = %s", (max_id + 1,))

    print(f"  {table}: migrated {len(rows)} row(s)")


def main():
    sqlite_path = sys.argv[1] if len(sys.argv) > 1 else "Studia.db"
    if not os.path.exists(sqlite_path):
        sys.exit(f"SQLite database not found: {sqlite_path}")

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row

    mysql_conn = get_mysql_connection()

    print(f"Migrating data from {sqlite_path} into MySQL...")
    try:
        for table in TABLES_IN_ORDER:
            migrate_table(sqlite_conn, mysql_conn, table)
        mysql_conn.commit()
        print("Migration complete.")
    except Exception:
        mysql_conn.rollback()
        print("Migration failed; MySQL changes were rolled back.")
        raise
    finally:
        sqlite_conn.close()
        mysql_conn.close()


if __name__ == "__main__":
    main()
