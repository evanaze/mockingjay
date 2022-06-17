"""A class for handling tweets."""


class Tweet:
    
    def __init__(self, content: str, id: int, user_id: int) -> None:
        """A constructor for the tweet datatype.
        
        :param content: The content of the tweet
        :param id: The ID of the tweet
        :param user_id: The ID of the user
        """
        self.content = content
        self.id = id
        self.user_id = user_id

    def add_timestamp(self, timestamp) -> None:
        """Add a timestamp."""
        self.timestamp = timestamp
