from dataclasses import dataclass


@dataclass
class MyTweet:
    """A tiny class for saving the tweet data that makes it easier to ingest

    :param id: The Tweet ID
    :param text: The text content of the ID
    :param author_id: The ID of the Tweet author
    """

    id: int
    text: str
    author_id: int

    def to_tuple(self):
        """Returns the data as a tuple"""
        return (self.id, self.author_id, self.text)
