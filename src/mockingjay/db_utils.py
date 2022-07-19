"""Functions for accessing the database."""
import os
import sqlite3
from pathlib import Path
from logging import getLogger

from mockingjay.exceptions import DbConnectionError
from mockingjay.tweet import MyTweet

BUFFER_SIZE = 250
logger = getLogger(__name__)


class DbConn:
    """A database connection object."""

    def __init__(
        self, db_path: str = os.path.join(Path(__file__).parents[2], "data/twitter.db")
    ):
        """Class for creating a database connection.

        :param db_path: The path to the Database object.
        """
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


class DbUtils:
    """DB utilities object."""

    def __init__(self, db_path: str) -> None:
        """DB Tools.

        :param db_path: Path to database object.
        """
        self.db_path = db_path
        if not os.path.isfile(db_path):
            self._init_db()

    def _init_db(self) -> None:
        """Initialize the database with tables."""
        with DbConn(self.db_path) as db_conn:
            cursor = db_conn.cursor()
            # raw tweets table
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS tweets_raw(
                tweetID INT PRIMARY KEY,
                authorID INT,
                text TEXT
                );"""
            )

            # processed tweets table
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS tweets_proc(
                tweetID INT PRIMARY KEY,
                authorID INT,
                text TEXT
                );"""
            )

            # users table
            cursor.execute(
                """CREATE TABLE IF NOT EXISTS users(
                authorID INT PRIMARY KEY,
                username TEXT,
                FOREIGN KEY (authorID)
                    REFERENCES tweets (authorID)
                );"""
            )

    def update_user(self) -> None:
        """Creates or updates a user with a given username"""
        params = {"author_id": self.author_id, "username": self.username}
        logger.debug("Updating user %s with ID %s", self.username, self.author_id)
        with DbConn(self.db_path) as db_conn:
            cursor = db_conn.cursor()
            cursor.execute(
                "INSERT INTO users(authorID, username) VALUES (:author_id, :username)"
                "ON CONFLICT (authorID) DO UPDATE SET username=:username",
                params,
            )

    def check_existing_user(self) -> bool:
        """Check whether we have tweets in the database for a set of users.

        :param author_id: The author ID to check for existing tweet data for
        :return: True if we have tweet data, false otherwise
        """
        with DbConn(self.db_path) as db_conn:
            logger.debug("Checking for existing tweets from ID %s", self.author_id)
            cursor = db_conn.cursor()
            cursor.execute(
                "SELECT EXISTS(SELECT 1 FROM tweets_raw WHERE authorID = (?));",
                (self.author_id,),
            )
            existing_tweets = cursor.fetchone()[0]
        return existing_tweets

    def most_recent_tweet(self, author_id: int) -> int:
        """Get the most recent tweet from a user."""
        with DbConn(self.db_path) as db_conn:
            logger.debug("Getting most recent tweet from ID %s", author_id)
            cursor = db_conn.cursor()
            cursor.execute(
                "SELECT tweetID FROM tweets_raw WHERE"
                "authorID = (?) ORDER BY tweetID DESC LIMIT 1;",
                (author_id,),
            )
            since = cursor.fetchone()[0]
        return since

    def write_tweets(self, tweets: list[MyTweet], table: str = "tweets_raw") -> None:
        """Write tweets to the database.

        :param table: The table name to write the tweets for
        """
        sql = f"INSERT INTO {table}(tweetID, authorID, text) VALUES (?, ?, ?)"
        queue = tweets.copy()
        with DbConn(self.db_path) as db_conn:
            cursor = db_conn.cursor()
            while queue:
                batch_size = min(len(queue), BUFFER_SIZE)
                logger.debug("Inserting %s tweets", batch_size)
                # Write the data in the queue
                for _ in range(batch_size):
                    tweet = queue.pop(0).to_tuple()
                    logger.debug("Inserting tweet %s", tweet)
                    cursor.execute(sql, tweet)
                db_conn.commit()
