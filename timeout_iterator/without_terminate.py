import datetime
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
    timeout expires. It simply stops yielding further items after the deadline.
    Cannot forcibly interrupt a task that is running between yields.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)
    iterator = iter(iterable)
    for item in iterator:
        if datetime.datetime.now() > end:
            _close_if_possible(iterator)
            break
        yield item
