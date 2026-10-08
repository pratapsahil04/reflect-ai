import sqlite3
from pathlib import Path
from datetime import datetime


DATABASE_PATH = Path("reflectai.db")


def get_connection():
    return sqlite3.connect(DATABASE_PATH)


def initialize_database():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS mood_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            mood_score INTEGER NOT NULL,
            primary_emotion TEXT NOT NULL,
            secondary_emotions TEXT,
            themes TEXT,
            confidence REAL
        )
        """
    )

    connection.commit()
    connection.close()


def save_mood(
    mood_score: int,
    primary_emotion: str,
    secondary_emotions: list[str],
    themes: list[str],
    confidence: float
):

    connection = get_connection()

    cursor = connection.cursor()

    timestamp = datetime.now().isoformat()

    cursor.execute(
        """
        INSERT INTO mood_entries (
            timestamp,
            mood_score,
            primary_emotion,
            secondary_emotions,
            themes,
            confidence
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            timestamp,
            mood_score,
            primary_emotion,
            ", ".join(secondary_emotions),
            ", ".join(themes),
            confidence
        )
    )

    connection.commit()
    connection.close()


def get_mood_entries():

    connection = get_connection()

    cursor = connection.cursor()

    cursor.execute(
        """
        SELECT
            id,
            timestamp,
            mood_score,
            primary_emotion,
            secondary_emotions,
            themes,
            confidence
        FROM mood_entries
        ORDER BY timestamp DESC
        """
    )

    rows = cursor.fetchall()

    connection.close()

    return rows