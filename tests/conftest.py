"""Configure the test suite."""
import pytest
from mockingjay.get_tweets import TweetReader


@pytest.fixture()
def fx_default_object():
    """Initialize the default TweetReader object."""
    return TweetReader(db_path="data/test.db")
