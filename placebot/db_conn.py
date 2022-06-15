"""Database interface class"""
import sqlite3
from typing import Optional


class DbConn:
    
    def __init__(self):
        """Class for interfacing with the SQLite3 database."""
        self.conn = sqlite3.connect("data/twitter.db")
        self.cursor = self.conn.cursor()
        self.queue = []
        self.init_db()

    def init_db(self):
        """Initialize the database with tables."""
        # tweets table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tweets(
            tweet_id INT PRIMARY KEY,
            user_id INT,
            tweet TEXT,
            timestamp TEXT
            );""")

        # users table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INT PRIMARY KEY,
            username TEXT,
            n_tweets INT
            );""")
        
    def get_most_recent_tweet(self, user_id: int) -> list:
        """Get the most recent tweet for a user."""
        self.cursor.execute("SELECT tweet_id FROM tweets WHERE user_id = (?);", user_id)
        return self.cursor.fetchone()

    def queue_tweets(self, tweets: dict) -> None:
        """Add tweets to the queue."""
        self.queue.append(tweets)
        self.write_tweets_to_db()

    def write_tweets_to_db(self) -> None:
        """Write queue to database"""
        while self.queue:
            self.cursor.execute("INSERT INTO tweets VALUES (?, ?)", ())
