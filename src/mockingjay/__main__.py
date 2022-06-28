"""CLI interface powered by click."""
import click
from src.mockingjay import get_tweets
from src.mockingjay.utils import check_handles


@click.command()
@click.argument("handles", help="The Twitter handles to emulate for.")
def cli(handles):
    if check_handles(handles):
        get_tweets(handles)
