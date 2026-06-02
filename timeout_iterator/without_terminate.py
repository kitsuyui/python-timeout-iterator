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
    """Timeout iterator

    This iterator times out after the specified number of seconds.
    This iterator cannot forcibly terminate a running task.
    It just ends without executing the next task.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)
    iterator = iter(iterable)
    for item in iterator:
        if datetime.datetime.now() > end:
            _close_if_possible(iterator)
            break
        yield item
