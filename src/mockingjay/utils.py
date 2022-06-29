"""Script containing utility functions."""
from mockingjay.db_conn import DbConn
from mockingjay.logger import get_logger
from mockingjay.twitter_conn import TwitterConn
from mockingjay.exceptions import UserNotFoundError


LOGGER = get_logger(__name__)


def check_handles(handles: list[str]) -> dict:
    """Checks that each Twitter handle is valid.

    :param handles: A list of Twitter handles to check for.
    :raises UserNotFoundError: Raises an error if the user
    """
    # Twitter connection
    tw_conn = TwitterConn()
    # Database connection
    db_conn = DbConn()
    user_ids = {}
    LOGGER.info(handles)
    for handle in handles:
        LOGGER.debug(f"Looking up user id for user {handle}")
        user = tw_conn.tweepy_client.get_user(username=handle)
        # Check for errors in finding the user
        if user.errors:
            msg = user.errors[0]["detail"]
            raise UserNotFoundError(msg)
        else:
            author_id = user.data["data"]["id"]
            LOGGER.debug(f"User {handle} has ID {author_id}")
            # Update the user table
            db_conn.update_user(author_id, handle)
            user_ids[handle] = author_id
    return user_ids
