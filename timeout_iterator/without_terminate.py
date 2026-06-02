import datetime
from collections.abc import Iterable, Iterator
from typing import TypeVar

from timeout_iterator._seconds import validate_timeout_seconds

T = TypeVar("T")


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def without_terminate(iterable: Iterable[T], seconds: float) -> Iterator[T]:
    """Timeout iterator

    This iterator times out after the specified number of seconds.
    This iterator cannot forcibly terminate a running task.
    It just ends without executing the next task.
    The timeout must be a positive finite number of seconds.
    """
    validate_timeout_seconds(seconds)
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)
    for item in iterable:
        if datetime.datetime.now() > end:
            break
        yield item
