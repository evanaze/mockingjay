class UserNotFoundError(Exception):
    """Raise an error when we were unable to find a user."""


class AuthTokenNotFoundError(Exception):
    """Raise an exception if Auth tokens are missing."""
