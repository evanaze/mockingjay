"""Form a connection to the Twitter API."""
import os
import tweepy
from exceptions import AuthTokenNotFoundError


class TwitterConn:
    """A simple object to form a connection with the Tweepy API."""

    def __init__(self):
        if bearer_token := os.getenv("TWITTER_BEARER_TOKEN"):
            self.tweepy_client = tweepy.Client(bearer_token)
        else:
            raise AuthTokenNotFoundError("Please export your bearer token.")
