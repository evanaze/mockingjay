"""Get tweets for a specified user."""
import os
from pathlib import Path
from typing import Optional
from logging import getLogger

# Third party packages
import tweepy

# Internal packages
from mockingjay.tweet import MyTweet
from mockingjay.db_utils import DbUtils
from mockingjay.process import Processor
from mockingjay.exceptions import AuthTokenNotFoundError, UserNotFoundError

logger = getLogger(__name__)


class TweetReader:
    """Read tweets from the Tweepy API and write to the database."""

    def __init__(
        self,
        usernames: Optional[list[str]] = None,
        db_path: str = os.path.join(Path(__file__).parents[2], "data/twitter.db"),
    ) -> None:
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
        self.db_path = db_path
        self.db_utils = DbUtils(db_path)
        self.since = None
        self.tweets = []
        self.user_ids = {}
        self.username = None
        self.author_id = None

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

    def check_newer_tweets(self) -> bool:
        """Check if the user has newer tweets we can scrape.

        :return: A boolean value for whether or not there are new tweets to scrape.
        """
        # Get the most recent tweet from our database
        self.since = self.db_utils.most_recent_tweet(self.author_id)
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
        """Get the user's tweets from the Tweepy API."""
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
            self.tweets.append(MyTweet(tweet.id, self.author_id, tweet.text))

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
            self.tweets = Processor(self.tweets).process_tweets()
            # Write clean tweets to DB
            self.write_tweets(table="tweets_proc")


if __name__ == "__main__":
    TweetReader().get_tweets()
