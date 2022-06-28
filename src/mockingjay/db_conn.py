"""Database interface class"""
import sqlite3

from pandas import DataFrame
from tweepy.tweet import Tweet

from mockingjay.logger import get_logger


LOGGER = get_logger(__name__)
# The number of inserts to execute in a batch
BUFFER_SIZE = 250


class DbConn:
    def __init__(self):
        """Class for interfacing with the SQLite3 database."""
        self.conn = sqlite3.connect("data/twitter.db")
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self) -> None:
        """Initialize the database with tables."""
        # raw tweets table
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS tweets_raw(
            tweetID INT PRIMARY KEY,
            authorID INT,
            tweet TEXT
            );"""
        )

        # processed tweets table
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS tweets(
            tweetID INT PRIMARY KEY,
            authorID INT,
            tweet TEXT
            );"""
        )

        # users table
        self.cursor.execute(
            """CREATE TABLE IF NOT EXISTS users(
            authorID INT PRIMARY KEY,
            username TEXT,
            FOREIGN KEY (authorID)
                REFERENCES tweets (authorID)
            );"""
        )

    def update_user(self, author_id: int, username: str) -> None:
        """Creates or updates a user with a given username"""
        params = {"author_id": author_id, "username": username}
        self.cursor.execute(
            """INSERT INTO users(authorID, username) VALUES (:author_id, :username)
                            ON CONFLICT (authorID) DO UPDATE SET username=:username""",
            params,
        )
        self.conn.commit()

    def check_existing_tweets(self, author_id: int) -> bool:
        """Check whether we have tweets in the database for a set of users.

        :param author_id: The author ID to check for existing tweet data for
        :return: True if we have tweet data, false otherwise
        """
        self.cursor.execute(
            "SELECT EXISTS(SELECT 1 FROM tweets_raw WHERE authorID = (?));",
            (author_id,),
        )
        existing_tweets = self.cursor.fetchone()[0]
        return existing_tweets

    def get_most_recent_tweet(self, author_id: int) -> int:
        """Get the ID of the most recent tweet for a user.

        :param author_id: The author ID to check for tweet data for
        :return: The tweet ID of the most recent tweet
        """
        self.cursor.execute(
            "SELECT tweetID FROM tweets_raw WHERE authorID = (?) ORDER BY tweetID DESC LIMIT 1;",
            (author_id,),
        )
        since = self.cursor.fetchone()[0]
        return since

    def batch_insert(
        self, sql: str, iterable: list[Tweet] | DataFrame, parse_function: function
    ) -> None:
        """Batch insert an iterable into the database.

        :param sql: The sql string to execute
        :param iterable:
        """
        while iterable:
            batch_size = min(len(iterable), BUFFER_SIZE)
            LOGGER.debug(f"Inserting {batch_size} tweets")
            # Write the data in the queue
            for _ in range(batch_size):
                iterable, data = parse_function(iterable)
                LOGGER.debug(f"Inserting tweet {data}")
                self.cursor.execute(sql, data)
            self.conn.commit()

    @staticmethod
    def parse_raw_tweets(
        tweets: list[Tweet],
    ) -> tuple[list[Tweet], tuple[str, int, str]]:
        tweet = tweets.pop(0)
        parse_raw_tweets = lambda tweet: (tweet.id, tweet.text)

    def write_raw_tweets(self, tweets: list[Tweet], author_id: int) -> None:
        """Write tweets to the database.

        :param tweets: The list of tweets to write to the database
        :param author_id: The ID of the author to write tweets for
        """
        sql = "INSERT INTO tweets_raw(tweetID, authorID, tweet) VALUES (?, ?, ?)"
        self.batch_insert(sql, tweets, parse_raw)

    def write_tweets(self, tweets: DataFrame, author_id: int) -> None:
        """Write a dataframe of cleaned tweets."""
        sql
