import datetime
import signal
from collections.abc import Iterable
from typing import TypeVar

T = TypeVar("T")


def _ensure_itimer_real_is_available() -> None:
    current_timer = signal.getitimer(signal.ITIMER_REAL)
    if current_timer == (0.0, 0.0):
        return

    message = "terminate() cannot run while ITIMER_REAL is already active"
    raise RuntimeError(message)


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def terminate(iterable: Iterable[T], seconds: float) -> Iterable[T]:
    """Timeout iterator

    This iterator forcibly terminates a task after the timeout expires.
    It cannot be used while another ITIMER_REAL timer is active.
    """
    _ensure_itimer_real_is_available()
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)

    def handler(signum: int, _frame: object) -> None:
        if signum != signal.SIGALRM or datetime.datetime.now() < end:
            return
        raise TimeoutError

    original_handler = signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)

    try:
        yield from iterable
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, original_handler)
