"""CLI interface powered by click."""
import sys
from logging import getLogger

import click

from mockingjay.get_tweets import TweetReader
from mockingjay.process import clean_all

# Initialize the root logger
logger = getLogger(__name__)


@click.group()
def cli():
    pass


@cli.command()
@click.argument("handles", nargs=-1)
def get_tweets(handles: list[str] = None) -> None:
    """Download tweets from the database.

    :param handles: A list of Twitter handles to check for.
    """
    logger.debug("Starting program.")
    # Check that an argument was supplied
    if not handles:
        click.echo("Please specify at least one Twitter username to emulate.")
        sys.exit(1)
    # Check that each handle is valid
    click.echo(f"Downloading data for user(s) {handles}")
    tweet_reader = TweetReader(handles)
    tweet_reader.check_handles()
    tweet_reader.get_tweets()

@cli.command()
def clean() -> None:
    """Cleans all raw data in the database."""
    clean_all()
