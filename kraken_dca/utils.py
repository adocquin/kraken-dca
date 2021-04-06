from datetime import datetime, timezone


def utc_unix_time_datetime(nix_time: int) -> datetime:
    """
    Takes utc nix time in seconds or nanoseconds and returns date as Datetime.

    :param nix_time: Nix time to convert to string date.
    :return: Converted date as string.
    """
    try:
        date = datetime.utcfromtimestamp(nix_time)
    except OSError:  # Case when unix time is in nanoseconds
        date = datetime.utcfromtimestamp(nix_time / 1000000000)
    return date


def current_utc_datetime() -> datetime:
    """
    Return current UTC date as Datetime in seconds precision.

    :return: Current date as Datetime.
    """
    return datetime.utcnow().replace(tzinfo=None, microsecond=0)


def current_utc_day_datetime() -> datetime:
    """
    Return current day datetime.

    :return: Current day as datetime.
    """
    current_date: datetime = current_utc_datetime()
    return current_date.replace(hour=0, minute=0, second=0, microsecond=0)


def datetime_as_utc_unix(date: datetime) -> int:
    """
    Transform passed datetime to utc unix time as int.

    :param date: Date to transform as datetime.
    :return: Date as int unix time.
    """
    return int(date.replace(tzinfo=timezone.utc).timestamp())
