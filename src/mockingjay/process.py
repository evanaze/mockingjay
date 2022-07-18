"""Process raw tweets."""
import os
from logging import getLogger

import toml
import pandas as pd

from mockingjay.tweet import MyTweet
from mockingjay.db_conn import DbConn
from mockingjay.db_utils import DbUtils

BUFFER_SIZE = 250
logger = getLogger(__name__)


class Processor:
    """Process the raw Tweets."""

    def __init__(self, tweets: list[MyTweet]) -> None:
        """An object for processing raw tweets.

        :param tweets: A list of Tweepy Tweet objects to clean
        """
        self.raw_tweets: list[MyTweet] = tweets
        self.author_ids: list[int] = [tweet.author_id for tweet in tweets]
        self.clean_df: pd.DataFrame = None

        self._load_config()
        
    def _load_config(self):
        """Load the configuration."""
        config_fpath = os.path.join(os.path.dirname(__file__), "config/config.toml")
        config = toml.load(config_fpath)
        self.min_words = config["process"]["min_words"]

    def clean_data(self) -> None:
        """Cleans the input data."""
        self.clean_df = (
            self.clean_df[~self.clean_df.text.str.contains("https")]
            .assign(
                n_words=self.clean_df.text.str.split().map(len),
                text=self.clean_df.text.str.strip(),
            )[lambda x: x.n_words >= self.min_words]
            .drop("n_words", axis=1)
            .reset_index(drop=True)
        )

    def _df_to_tweets(self) -> None:
        """Turn a DataFrame of Tweets back to Tweet objects"""
        self.clean_tweets = [0] * len(self.clean_df)
        for i, row in enumerate(self.clean_df.itertuples(index=False)):
            self.clean_tweets[i] = MyTweet(row.id, row.author, row.text)

    def process_tweets(self) -> list[MyTweet]:
        """Process a list of tweets.

        :return: A list of processed tweets
        """
        # Create a Dataframe of tweets
        self.clean_df = pd.DataFrame(
            [(tweet.tweet_id, tweet.author_id, tweet.text) for tweet in self.raw_tweets], columns=["id", "author", "text"]
        )
        # Clean the Tweets
        self.clean_data()
        # Turn Dataframe into a list of tweet objects
        self._df_to_tweets()
        return self.tweets


def clean_all(db_path: str) -> None:
    """Clean all data in the raw table and re-insert into the processed table.

    :param db_path: Path to the database to clean.
    """
    with DbConn(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tweets_raw;")
        raw_tweets = cursor.fetchall()
    # Turn tweets into MyTweets objects
    print(raw_tweets)
    raw_tweets = [MyTweet()]
    
    # Process the raw tweets
    proc = Processor(raw_tweets)
    clean_tweets = proc.process_tweets()
    # Insert clean tweets into the database
    
