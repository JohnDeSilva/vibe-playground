import sqlite3
import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)

DB_FILE = Path.home() / ".config" / "vibe-streamer" / "library.db"


def get_connection():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_FILE)


def init_db():
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS library (
                    series TEXT,
                    season TEXT,
                    episode TEXT,
                    path TEXT
                )
            """)
            conn.commit()
    except Exception as e:
        logger.error(f"Error initializing database: {e}")


def load_library() -> Dict[str, Any]:
    """
    Loads the library from the database and reconstructs the dictionary format.
    """
    library = {}
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT series, season, episode, path FROM library")
            rows = cursor.fetchall()

            for series, season, episode, path in rows:
                if series not in library:
                    library[series] = {}
                if season not in library[series]:
                    library[series][season] = []

                library[series][season].append({"name": episode, "path": path})

            # Ensure episodes are sorted alphabetically
            for series in library:
                for season in library[series]:
                    library[series][season].sort(key=lambda x: x["name"])

    except Exception as e:
        logger.error(f"Error loading library from database: {e}")

    return library


def save_library(library: Dict[str, Any]):
    """
    Clears the database and completely populates it with the given library dictionary.
    """
    try:
        with get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM library")

            for series, seasons in library.items():
                for season, episodes in seasons.items():
                    for ep in episodes:
                        cursor.execute(
                            "INSERT INTO library (series, season, episode, path) VALUES (?, ?, ?, ?)",
                            (series, season, ep["name"], ep["path"]),
                        )
            conn.commit()
            logger.info("Library successfully saved to database.")
    except Exception as e:
        logger.error(f"Error saving library to database: {e}")
