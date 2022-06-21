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
            tweetID INT PRIMARY KEY,
            authorID INT,
            tweet TEXT,
            timestamp TEXT
            FOREIGN KEY (authorID)
                REFERENCES users (authorID)
            );""")

        # users table
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS users(
            authorID INT PRIMARY KEY,
            username TEXT
            );""")
        
    def update_user(self, author_id: int, username: str) -> None:
        """Creates or updates a user with a given username"""
        params = {"author_id": author_id, "username": username}
        self.cursor.execute("""INSERT INTO users VALUES (:author_id, :username)
                            ON CONFLICT (author_id) DO UPDATE SET username=:username""", params)
        self.conn.commit()
        
    def get_most_recent_tweet(self, author_id: int) -> int:
        """Get the ID of the most recent tweet for a user.
        
        :return: The tweet ID of the most recent tweet
        """
        self.cursor.execute("SELECT tweetID FROM tweets WHERE authorID = (?);", (author_id))
        tweet = self.cursor.fetchone()[0]
        return tweet.id
    
    def queue_tweet(self, tweet: dict) -> None:
        """Add tweets to the queue."""
        self.queue.append((tweet.id, tweet.author_id, tweet.text, tweet.timestamp))

    def write_tweets(self) -> None:
        """Write queue to database"""
        while self.queue:
            # Write the data in the queue
            for _ in range(min(len(self.queue), BUFFER_SIZE)):
                tweet_id, author_id, text, timestamp = self.queue.pop(0)
                self.cursor.execute("INSERT INTO tweets VALUES (?, ?, ?, ?)", (tweet_id, author_id, text, timestamp))
                self.queue.task_done()
            self.conn.commit()
