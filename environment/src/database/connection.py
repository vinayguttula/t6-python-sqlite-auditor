"""Database connection management."""
import sqlite3

def get_connection(db_path: str) -> sqlite3.Connection:
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
