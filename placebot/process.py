"""Process raw tweets."""
import toml
import pandas as pd
from tweepy.tweet import Tweet

# Load the configuration
config = toml.load("placebot/config.toml")
min_words = config["process"]["min_words"]


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """Cleans the input data.

    :param df: A dataframe of raw tweets and tweet IDs
    :return: A cleaned Dataframe of tweets
    """
    return (
        df[~df.text.str.contains("https")]
        .assign(n_words=df.text.str.split().map(len), text=df.text.str.strip())[
            lambda x: x.n_words >= min_words
        ]
        .drop("n_words", axis=1)
        .reset_index(drop=True)
    )


def process_tweets(raw_tweets: list[Tweet]) -> pd.DataFrame:
    """Process a list of tweets.

    :param tweets: A list of Tweepy Tweet objects to clean
    :return: A cleaned DataFrame of tweets
    """
    # Create a Dataframe of tweets
    tweets = [(tweet.id, tweet.text) for tweet in raw_tweets]
    df = pd.DataFrame(tweets, columns=["id", "text"])
    return clean_data(df)
