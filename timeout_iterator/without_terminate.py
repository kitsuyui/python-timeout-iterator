import datetime
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def without_terminate(iterable: Iterable[T], seconds: float) -> Iterator[T]:
    """Timeout iterator that stops gracefully without raising TimeoutError.

    Unlike `terminate`, this function does NOT raise TimeoutError when the
    timeout expires. It simply stops yielding further items after the deadline.
    Cannot forcibly interrupt a task that is running between yields.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)
    for item in iterable:
        if datetime.datetime.now() > end:
            break
        yield item
