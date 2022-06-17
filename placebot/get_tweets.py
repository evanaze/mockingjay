"""Get tweets for a specified user."""
import os
from logging import getLogger
from typing import Optional

# Third party packages
import tweepy

# Internal packages
from db_conn import DbConn
from tweet import Tweet
from exceptions import UserNotFoundError, AuthTokenNotFoundError

LOGGER = getLogger(__name__)


class TweetReader:

    def __init__(self, usernames: list = ["PIaceboAddict"]) -> None:
        """Read the tweets from a user or set of users.

        :param usernames: The list of usernames to scrape tweets for.
        """
        self.usernames = usernames
        if bearer_token := os.getenv("TWITTER_BEARER_TOKEN"):
            self.client = tweepy.Client(bearer_token)
        else:
            raise AuthTokenNotFoundError("Please export your bearer token.")
        self.db_conn = DbConn()

    def get_user_ids(self) -> None:
        """Get the user IDs of the users Twitter handles."""
        self.user_ids = {}
        for username in self.usernames:
            LOGGER.debug(f"Looking up user id for user {username}")
            user = self.client.get_user(username=username)
            if user.errors:
                msg = user.errors[0]["detail"]
                raise UserNotFoundError(msg)
            else:
                user_id = user.data["data"]["id"]
                LOGGER.debug(f"User {username} has ID {user_id}")
                self.user_ids[username] = user_id
                
    def existing_data(self) -> Optional[int]:
        """Check if there already exists data for the user."""
        pass

    def get_tweets_user_id(self):
        """Get the user's tweets."""
        tweets = {"user_id": self.user_id, "tweets": []}
        LOGGER.debug(f"Getting tweets for user {self.username} since tweet {self.since}")
        # Get tweets, optionally after a tweet ID
        for tweet in tweepy.Paginator(self.client.get_users_tweets, id=self.user_id, exclude=["retweets", "replies"],
                                since=self.since, max_results=10, user_fields="created_at").flatten(limit=250):
            tweets["tweets"].append({"tweet": tweet, "id": tweet.id})
        # Write the tweets to the database
        self.db_conn.write_tweets_to_db(tweets)

    def get_tweets_users(self) -> None:
        """Get all tweets for the data set."""
        # Get user ID's
        self.get_user_ids()
        for self.username in self.user_ids:
            self.user_id = self.user_ids[self.username]
            # Check for existing tweet data for the user in our database
            if (self.check_existing_data() := self.since):
                # Check if there are newer tweets we can scrape
                if self.newer_tweets():
                    self.get_tweets_user_id()


if __name__ == "__main__":
    TweetReader().get_tweets_users()
