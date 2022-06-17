"""Database interface class"""
import sqlite3
from typing import Optional

# The number of inserts to execute in a batch
BUFFER_SIZE = 250


class DbConn:
    
    def __init__(self):
        """Class for interfacing with the SQLite3 database."""
        self.conn = sqlite3.connect("data/twitter.db")
        self.cursor = self.conn.cursor()
        self.queue = []
        self.init_db()

    def init_db(self) -> None:
        """Initialize the database with tables."""
        # tweets table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS tweets(
            tweet_id INT PRIMARY KEY,
            user_id INT,
            tweet TEXT,
            timestamp TEXT
            FOREIGN KEY (user_id)
                REFERENCES users (user_id)
            );""")

        # users table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            user_id INT PRIMARY KEY,
            username TEXT
            );""")
        
    def get_most_recent_tweet(self, user_id: int) -> int:
        """Get the ID of the most recent tweet for a user.
        
        :return: The tweet ID of the most recent tweet
        """
        self.cursor.execute("SELECT tweet_id FROM tweets WHERE user_id = (?);", user_id)
        tweet = self.cursor.fetchone()[0]
        return tweet.id

    def write_tweets_to_db(self, user_id: int, tweets: dict) -> None:
        """Write queue to database"""
        self.queue.extend(tweets)
        while self.queue:
            # Write the data in the queue
            for i in range(min(len(self.queue, BUFFER_SIZE))):
                tweet = self.queue.pop(0)
                tweet_id, author_id, text, timestamp = tweet.id, tweet.author_id, tweet.text, tweet.timestamp
                self.cursor.execute("INSERT INTO tweets VALUES (?, ?, ?, ?)", (tweet_id, author_id, text, timestamp))
            self.conn.commit()

