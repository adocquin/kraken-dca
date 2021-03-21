from datetime import datetime
import pytz


def unix_time_datetime(nix_time: int) -> datetime:
    """
    Takes nix time in seconds or nanoseconds and returns date as Datetime.

    :param nix_time: Nix time to convert to string date.
    :return: Converted date as string.
    """
    try:
        date = datetime.utcfromtimestamp(nix_time)
    except OSError:  # Case when unix time is in nanoseconds
        date = datetime.utcfromtimestamp(nix_time/1000000000)
    return date


def current_datetime() -> datetime:
    """
    Return current date as string.

    :return: Current date as Datetime.
    """
    date = datetime.now().astimezone(pytz.utc)
    return date

