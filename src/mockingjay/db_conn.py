"""Database interface class"""
import os
import sqlite3
from pathlib import Path
from logging import getLogger

from mockingjay.exceptions import DbConnectionError

logger = getLogger(__name__)


class DbConn:
    """A database connection object."""

    def __init__(
        self, db_path: str = os.path.join(Path(__file__).parents[2], "data/twitter.db")
    ):
        """Class for creating a database connection."""
        self.db_path = db_path
        self.conn: sqlite3.Connection = None

    def __enter__(self):
        """Enter the DB connection."""
        logger.info("Connecting to DB %s", self.db_path)
        self.conn = sqlite3.connect(self.db_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the DB connection.

        :param exc_type: The exit type.
        :param exc_val: The exit value.
        :param exc_tb: The exit traceback.
        """
        if exc_tb is None:
            self.conn.commit()
        else:
            self.conn.rollback()
            raise DbConnectionError("Database connection error")
        self.conn.close()
