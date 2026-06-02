import datetime
import signal
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def terminate(iterable: Iterable[T], seconds: float) -> Iterable[T]:
    """Timeout iterator

    This iterator forcibly terminates a task after the timeout expires.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)

    def handler(signum: int, _frame: object) -> None:
        if signum != signal.SIGALRM or datetime.datetime.now() < end:
            return
        elapsed = (datetime.datetime.now() - now).total_seconds()
        raise TimeoutError(
            f"timed out after {elapsed:.3f}s (limit: {seconds}s)",
        )

    original_handler = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)

    try:
        yield from iterable
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, original_handler)
