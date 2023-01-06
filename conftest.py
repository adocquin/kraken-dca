import logging

import pytest


@pytest.fixture()
def logging_capture(caplog):
    """Test fixture that captures logging output at INFO level.

    Filters out any log messages that do not originate from krakendca.

    Use logging_capture.read() in your test to retrieve the current log output.
    """
    caplog.set_level(logging.INFO)

    class FilteredLog:
        def read(self) -> str:
            return (
                "\n".join(
                    record.message
                    for record in caplog.records
                    if record.name.startswith("krakendca")
                )
                + "\n"
            )

    return FilteredLog()
