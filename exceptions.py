"""Utility module for defining our own custom exceptions."""

class HumanReadableError(Exception):
    """This is our custom exception for better user experience on error notifications."""
    pass

def raise_readable_error(message):
    """Raise the human readable error message."""
    raise HumanReadableError(message)

def is_human_readable(exception):
    """Check if exception is an instance of HumanReadableError."""
    return isinstance(exception, HumanReadableError)
