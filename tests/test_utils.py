from kraken_dca import (
    utc_unix_time_datetime,
    current_utc_datetime,
    current_utc_day_datetime,
    datetime_as_utc_unix,
    find_nested_dictionary,
)
from datetime import datetime
import pytest
from freezegun import freeze_time
import pytz


def test_utc_unix_time_datetime():
    # Test utc unix time in second.
    date_test = utc_unix_time_datetime(1617721936)
    date = datetime(2021, 4, 6, 15, 12, 16)
    assert date_test == date

    # Test non utc (utc+2) time in second.
    date_test = utc_unix_time_datetime(1617714736)
    date = datetime(2021, 4, 6, 15, 12, 16)
    assert date_test != date

    # Test utc unix time in nanosecond.
    date_test = utc_unix_time_datetime(1617728136000000000)
    date = datetime(2021, 4, 6, 16, 55, 36)
    assert date_test == date

    # Raise an error if datetime not in second or nanosecond.
    with pytest.raises(ValueError) as e_info:
        utc_unix_time_datetime(1617728136000000)
    assert "year 51265733 is out of range" in str(e_info.value)


@freeze_time("2012-01-14 18:10:34.089891", tz_offset=2)
def test_current_utc_datetime():
    # Test current time in utc without microseconds.
    date = datetime(2012, 1, 14, 18, 10, 34)
    assert current_utc_datetime() == date


@freeze_time("2012-01-13 23:10:34.069731", tz_offset=2)
def test_current_utc_day_datetime():
    # Test current time truncated to utc day.
    date = datetime(2012, 1, 13)
    assert current_utc_day_datetime() == date


def test_datetime_as_utc_unix():
    # Test utc datetime correctly transformed to unix unix time.
    date = datetime(2021, 4, 6, 17, 12, 16, 0, pytz.timezone("UTC"))
    assert datetime_as_utc_unix(date) == 1617729136

    # Test utc+2 date correctly transformed to unix unix time.
    date = datetime(2021, 4, 6, 17, 12, 16, 0, pytz.timezone("Asia/Shanghai"))
    assert datetime_as_utc_unix(date) == 1617729136


def test_find_nested_dictionary():
    dictionary = {
        "dict1": {},
        "dict2": {"key1": "value1", "key2": "value2"},
        "key3": {"key1": "value1"},
    }
    nested_dictionary = find_nested_dictionary(dictionary, "dict2")
    assert nested_dictionary == {"key1": "value1", "key2": "value2"}
    nested_dictionary = find_nested_dictionary(dictionary, "dict4")
    assert nested_dictionary is None
