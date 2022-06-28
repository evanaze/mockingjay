"""CLI interface powered by click."""
import click
from mockingjay.get_tweets import TweetReader
from mockingjay.utils import check_handles


@click.command()
@click.argument("handles")
def cli(handles: list[str]) -> None:
    """Defines the CLI.
    
    :param handles: A list of Twitter handles to check for.
    """
    # Check that an argument was supplied
    if not handles:
        click.echo("Please specify at least one Twitter username to emulate.")
        exit(1)
    # Check that each handle is valid
    if check_handles(handles):
        tweet_reader = TweetReader(handles)
        tweet_reader.get_tweets()
