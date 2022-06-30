"""Get tweets for a specified user."""
# Third party packages
import tweepy

# Internal packages
from mockingjay.tweet import MyTweet
from mockingjay.db_conn import DbConn
from mockingjay.process import Process
from mockingjay.logger import get_logger
from mockingjay.utils import check_handles
from mockingjay.twitter_conn import TwitterConn


logger = get_logger(__name__)


class TweetReader(TwitterConn):
    def __init__(self, usernames: list[str] = ["PIaceboAddict"]) -> None:
        """Read the tweets from a user or set of users.

        :param usernames: The list of usernames to scrape tweets for.
        """
        super().__init__()
        self.usernames = usernames
        self.since = None
        self.db_conn = DbConn()

    def check_newer_tweets(self) -> bool:
        """Check if the user has newer tweets we can scrape.

        :return: A boolean value for whether or not there are new tweets to scrape.
        """
        # Get the most recent tweet from our database
        most_recent_db = self.db_conn.get_most_recent_tweet(self.author_id)
        logger.debug(f"Most recent recorded tweet: {most_recent_db}")
        # Get the user's most recent tweet on Twitter
        most_recent_tweets = self.tweepy_client.get_users_tweets(
            id=self.author_id,
            exclude=["retweets", "replies"],
            since_id=most_recent_db,
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

    def get_tweets(self) -> None:
        """Get all tweets for the data set."""
        # Get user ID's
        self.user_ids = check_handles(self.usernames)
        for self.username in self.user_ids:
            self.author_id = self.user_ids[self.username]
            # Check for existing tweet data for the user in our database
            if self.db_conn.check_existing_tweets(self.author_id):
                logger.info(
                    f"Found existing tweets in the database for user {self.username}"
                )
                # Check if the user has made new tweets we can scrape
                if self.check_newer_tweets():
                    logger.info(f"New tweets for user {self.username}")
                    self.get_users_tweets()
                else:
                    logger.info(f"No new tweets to scrape for user {self.username}")
                    continue
            else:
                logger.info(
                    f"No existing tweets found in the database for user {self.username}"
                )
                self.get_users_tweets()
            # Write raw tweets to database
            self.db_conn.write_tweets(self.tweets)
            # Clean the tweets
            clean_tweets = Process(self.tweets).process_tweets()
            # Write clean tweets to DB
            self.db_conn.write_tweets(clean_tweets, table="tweets_proc")


if __name__ == "__main__":
    TweetReader().get_tweets()
