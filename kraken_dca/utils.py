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


def find_first_nested_dictionary(nested_dict: dict, elem: object):
    """
    Find first dictionary with key equals to elem in a nested dictionary.

    :param nested_dict:  Nested dictionary to find the element.
    :param elem: Key element to find.
    :return: First dictionary found in the nested dictionary with key equals to elem.
    """
    nested_dictionary = {
        elem_key: elem_dict
        for elem_key, elem_dict in nested_dict.items()
        if elem_key == elem
    }
    dictionary = nested_dictionary.get(elem)
    return dictionary
