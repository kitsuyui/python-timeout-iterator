import time
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def without_terminate(iterable: Iterable[T], seconds: float) -> Iterable[T]:
    """Timeout iterator

    This iterator times out after the specified number of seconds.
    This iterator cannot forcibly terminate a running task.
    It just ends without executing the next task.
    """
    end = time.monotonic() + seconds
    for item in iterable:
        if time.monotonic() > end:
            break
        yield item
