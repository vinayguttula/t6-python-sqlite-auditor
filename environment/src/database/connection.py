"""Database connection management."""
import sqlite3
import logging
import typing

logger = logging.getLogger(__name__)

def get_connection(db_path: str) -> typing.Optional[sqlite3.Connection]:
    """
    Establish and return a connection to the SQLite database.
    
    Args:
        db_path (str): The file path to the SQLite database.
        
    Returns:
        sqlite3.Connection: The active database connection object, or None if failed.
    """
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.Error as e:
        logger.error(f"Failed to connect to database at {db_path}: {e}")
        return None
