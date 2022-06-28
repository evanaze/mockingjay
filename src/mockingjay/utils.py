"""Script containing utility functions."""
from src.mockingjay.twitter_conn import TwitterConn
from src.mockingjay.exceptions import UserNotFoundError
from src.mockingjay.logger import get_logger


LOGGER = get_logger(__name__)


def check_handles(handles: list[str]) -> dict:
    """Checks that each Twitter handle is valid.

    :param handles: A list of Twitter handles to check for.
    :raises UserNotFoundError: Raises an error if the user 
    """
    conn = TwitterConn()
    user_ids = {}
    for handle in handles:
        LOGGER.debug(f"Looking up user id for user {handle}")
        user = conn.tweepy_client.get_user(username=handle)
        # Check for errors in finding the user
        if user.errors:
            msg = user.errors[0]["detail"]
            raise UserNotFoundError(msg)
        else:
            author_id = user.data["data"]["id"]
            LOGGER.debug(f"User {username} has ID {author_id}")
            # Update the user table
            self.db_conn.update_user(author_id, username)
            self.user_ids[username] = author_id
    return user_ids


