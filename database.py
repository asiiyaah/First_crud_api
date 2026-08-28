import os
from datetime import datetime

import psycopg
from psycopg.rows import dict_row
from dotenv import load_dotenv


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")


def get_connection():
    return psycopg.connect(
        DATABASE_URL,
        row_factory=dict_row
    )


def init_db():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT FALSE,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()["count"]

    if count == 0:
        now = datetime.now().isoformat()

        sample_tasks = [
            ("Buy groceries", False, now, now),
            ("Do homework", True, now, now),
            ("Do the dishes", False, now, now)
        ]

        cursor.executemany(
            """
            INSERT INTO tasks
                (title, done, created_at, updated_at)
            VALUES
                (%s, %s, %s, %s)
            """,
            sample_tasks
        )

    connection.commit()
    connection.close()