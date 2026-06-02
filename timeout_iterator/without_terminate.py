import datetime
from collections.abc import Iterable, Iterator
from typing import TypeVar

T = TypeVar("T")


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def without_terminate(iterable: Iterable[T], seconds: float) -> Iterator[T]:
    """Timeout iterator that stops yielding items once the deadline elapses.

    The timeout is checked *after* each item is fetched from the upstream
    iterator, not before. This means that if the deadline expires while a
    fetch is in progress (or just after one completes), the fetched item is
    silently dropped — consumed from the upstream but not yielded to the
    caller. At most one item may be lost this way at the boundary.

    Unlike terminate(), this function never raises TimeoutError and does not
    use signals, so it is safe to use in environments that restrict SIGALRM.
    The trade-off is that it cannot interrupt a blocking upstream fetch.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)
    for item in iterable:
        if datetime.datetime.now() > end:
            break
        yield item
