"""Process raw tweets."""
import os
from logging import getLogger

import toml
import pandas as pd
from tweepy.tweet import Tweet

from mockingjay.tweet import MyTweet


logger = getLogger(__name__)


class Process:
    """Process the raw Tweets."""

    def __init__(self, tweets: list[Tweet]) -> None:
        """An object for processing raw tweets.

        :param tweets: A list of Tweepy Tweet objects to clean
        """
        self.tweets = tweets
        self.author_id = tweets[0].author_id
        # Load the configuration
        config_fpath = os.path.join(os.path.dirname(__file__), "config/config.toml")
        config = toml.load(config_fpath)
        self.min_words = config["process"]["min_words"]
        self.clean_df: pd.DataFrame = None

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

    def df_to_tweets(self) -> None:
        """Turn a DataFrame of Tweets back to Tweet objects"""
        self.tweets = [0] * len(self.clean_df)
        for i, row in enumerate(self.clean_df.itertuples(index=False)):
            self.tweets[i] = MyTweet(row.id, row.text, self.author_id)

    def process_tweets(self) -> list[MyTweet]:
        """Process a list of tweets.

        :return: A list of processed tweets
        """
        # Create a Dataframe of tweets
        self.clean_df = pd.DataFrame(
            [(tweet.id, tweet.text) for tweet in self.tweets], columns=["id", "text"]
        )
        # Clean the Tweets
        logger.info("Cleaning data for user %s", self.author_id)
        self.clean_data()
        # Turn Dataframe into a list of tweet objects
        self.df_to_tweets()
        return self.tweets
