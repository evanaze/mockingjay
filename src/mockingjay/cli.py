"""CLI interface powered by click."""
import sys
from logging import getLogger

import click
from mockingjay.get_tweets import TweetReader

# Initialize the root logger
logger = getLogger(__name__)


@click.command()
@click.argument("handles", nargs=-1)
def cli(handles: list[str] = None) -> None:
    """Defines the CLI.

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
