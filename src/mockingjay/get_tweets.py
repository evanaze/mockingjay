"""Get tweets for a specified user."""
import os
from pathlib import Path
from typing import Optional
from logging import getLogger

# Third party packages
import tweepy

# Internal packages
from mockingjay.tweet import MyTweet
from mockingjay.db_conn import DbConn
from mockingjay.process import Process
from mockingjay.exceptions import AuthTokenNotFoundError, UserNotFoundError

BUFFER_SIZE = 250
logger = getLogger(__name__)


class TweetReader:
    """Read tweets from the Tweepy API and write to the database."""

    def __init__(self, usernames: Optional[list[str]] = None, 
                 db_path: str = os.path.join(Path(__file__).parents[2], "data/twitter.db")) -> None:
        """Read the tweets from a user or set of users.

        :param usernames: The list of usernames to scrape tweets for.
        """
        super().__init__()
        if not usernames:
            self.usernames = ["PIaceboAddict"]
        else:
            self.usernames = usernames
        if bearer_token := os.getenv("TWITTER_BEARER_TOKEN"):
            self.tweepy_client = tweepy.Client(bearer_token)
        else:
            raise AuthTokenNotFoundError("Please export your bearer token.")
        # Check if database needs to be initialized
        self.db_path = db_path
        if not os.path.isfile(db_path):
            self._init_db()
        self.since = None
        self.tweets = []
        self.user_ids = {}
        self.username = None
        self.author_id = None

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
            db_conn.commit()

    def check_handles(self) -> None:
        """Checks that each Twitter handle is valid."""
        for self.username in self.usernames:
            logger.debug("Looking up user id for user %s", self.username)
            user = self.tweepy_client.get_user(username=self.username)
            # Check for errors in finding the user
            if user.errors:
                msg = user.errors[0]["detail"]
                raise UserNotFoundError(msg)
            self.author_id = user.data["data"]["id"]
            logger.debug("User %s has ID %s", self.username, self.author_id)
            # Update the user table
            self.update_user()
            self.user_ids[self.username] = self.author_id

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

    def check_newer_tweets(self) -> bool:
        """Check if the user has newer tweets we can scrape.

        :return: A boolean value for whether or not there are new tweets to scrape.
        """
        # Get the most recent tweet from our database
        with DbConn(self.db_path) as db_conn:
            logger.debug("Getting most recent tweet from ID %s", self.author_id)
            cursor = db_conn.cursor()
            cursor.execute(
                "SELECT tweetID FROM tweets_raw WHERE"
                "authorID = (?) ORDER BY tweetID DESC LIMIT 1;",
                (self.author_id,),
            )
            self.since = cursor.fetchone()[0]
        # Get the user's most recent tweet on Twitter
        most_recent_tweets = self.tweepy_client.get_users_tweets(
            id=self.author_id,
            exclude=["retweets", "replies"],
            since_id=self.since,
            max_results=5,
        )
        # Check if there are new tweets
        return int(most_recent_tweets.meta["result_count"]) != 0

    def get_users_tweets(self) -> None:
        """Get the user's tweets."""
        msg = f"Getting tweets for user {self.username}"
        if self.since:
            msg += f" since tweet {self.since}"
        logger.debug(msg)
        # Get tweets, optionally after a tweet ID
        self.tweets = []
        for tweet in tweepy.Paginator(
            self.tweepy_client.get_users_tweets,
            id=self.author_id,
            exclude=["retweets", "replies"],
            since_id=self.since,
        ).flatten():
            self.tweets.append(MyTweet(tweet.id, tweet.text, self.author_id))

    def write_tweets(self, table: str = "tweets_raw") -> None:
        """Write tweets to the database.

        :param table: The table name to write the tweets for
        """
        sql = f"INSERT INTO {table}(tweetID, authorID, text) VALUES (?, ?, ?)"
        queue = self.tweets.copy()
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

    def get_tweets(self) -> None:
        """Get all tweets for the data set."""
        # Get user ID's for each username
        self.check_handles()
        for self.username in self.user_ids:
            self.author_id = self.user_ids[self.username]
            # Variable to record the last tweet for the user in our database
            self.since = None
            # Check for existing tweet data for the user in our database
            if self.check_existing_user():
                logger.info(
                    "Found existing tweets in the database for user %s", self.username
                )
                # Check if the user has made new tweets we can scrape
                if self.check_newer_tweets():
                    logger.info("New tweets for user %s", self.username)
                    self.get_users_tweets()
                else:
                    logger.info("No new tweets to scrape for user %s", self.username)
                    continue
            else:
                logger.info(
                    "No existing tweets found in the database for user %s",
                    self.username,
                )
                self.get_users_tweets()
            # Write raw tweets to database
            self.write_tweets()
            # Clean the tweets
            self.tweets = Process(self.tweets).process_tweets()
            # Write clean tweets to DB
            self.write_tweets(table="tweets_proc")


if __name__ == "__main__":
    TweetReader().get_tweets()
