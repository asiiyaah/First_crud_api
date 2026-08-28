import sqlite3
from datetime import datetime


DATABASE_NAME = "tasks.db"


def get_connection():
    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        now = datetime.now().isoformat()

        sample_tasks = [
            ("Buy groceries", 0, now, now),
            ("Do homework", 1, now, now),
            ("Do the dishes", 0, now, now)
        ]

        cursor.executemany(
            """
            INSERT INTO tasks
            (title, done, created_at, updated_at)
            VALUES (?, ?, ?, ?)
            """,
            sample_tasks
        )

    connection.commit()
    connection.close()