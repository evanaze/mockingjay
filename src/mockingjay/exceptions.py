"""Exceptions for the Mockingjay library."""


class UserNotFoundError(Exception):
    """Raise an error when we were unable to find a user."""


class AuthTokenNotFoundError(Exception):
    """Raise an exception if Auth tokens are missing."""


class DbConnectionError(Exception):
    """Raise an error when we cannot connect to a database."""
