import time
from collections.abc import Iterable, Iterator
from typing import Protocol, TypeGuard, TypeVar

T = TypeVar("T")


class _Closeable(Protocol):
    def close(self) -> None: ...


def _is_closeable(value: object) -> TypeGuard[_Closeable]:
    return callable(getattr(value, "close", None))


def _close_if_possible(value: object) -> None:
    if _is_closeable(value):
        value.close()


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def without_terminate(iterable: Iterable[T], seconds: float) -> Iterator[T]:
    """Timeout iterator that stops gracefully without raising TimeoutError.

    Unlike `terminate`, this function does NOT raise TimeoutError when the
    timeout expires and does not use signals, so it is safe to use in
    environments that restrict SIGALRM. It simply stops yielding further
    items after the deadline.

    The timeout is checked *after* each item is fetched from the upstream
    iterator, not before. This means that if the deadline expires while a
    fetch is in progress (or just after one completes), the fetched item is
    silently dropped — consumed from the upstream but not yielded to the
    caller. At most one item may be lost this way at the boundary.

    The trade-off is that it cannot forcibly interrupt a blocking upstream
    fetch or a task that is running between yields.
    """
    end = time.monotonic() + seconds
    iterator = iter(iterable)
    for item in iterator:
        if time.monotonic() > end:
            _close_if_possible(iterator)
            break
        yield item
