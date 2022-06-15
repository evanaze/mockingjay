"""Get tweets for a specified user."""
import os
from logging import getLogger
from concurrent.futures import ThreadPoolExecutor

# Third party packages
import tweepy

LOGGER = getLogger(__name__)


class UserNotFoundError(Exception):
    """Raise an error when we were unable to find a user."""


class TweetReader:

    def __init__(self, usernames: list = ["PIaceboAddict"]) -> None:
        """Read the tweets from a user or set of users."""
        self.usernames = usernames
        self.client = tweepy.Client(os.getenv("TWITTER_BEARER_TOKEN"))

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

    def get_tweets_user_id(self, user_id: str) -> None:
        """Get the user's tweets.
        
        :param user_id: The user's Twitter ID to fetch tweets
        :type user_id: str
        """
        for response in tweepy.pagination(self.client.get_users_tweets, id=user_id, 
                                          exclude="retweets", max_results = 5):
            LOGGER.info(response)

    def get_tweets_users(self) -> None:
        """Get all tweets for the data set."""
        # Get user ID's
        self.get_user_ids()
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(self.get_tweets_user_id, list(self.user_ids.values()))
            for result in results:
                LOGGER.info(result)


if __name__ == "__main__":
    TweetReader().get_tweets_users()
