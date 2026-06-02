import signal
import threading
import time
from collections.abc import Iterable, Iterator
from typing import TypeVar

from timeout_iterator._seconds import validate_timeout_seconds

T = TypeVar("T")


def _ensure_itimer_real_is_available() -> None:
    current_timer = signal.getitimer(signal.ITIMER_REAL)
    if current_timer == (0.0, 0.0):
        return

    message = "terminate() cannot run while ITIMER_REAL is already active"
    raise RuntimeError(message)


def _require_main_thread() -> None:
    if threading.current_thread() is not threading.main_thread():
        raise ValueError(
            "terminate() must be called from the main thread; "
            "signal.signal() and signal.setitimer() are main-thread-only "
            "APIs. Use without_terminate() for thread-safe timeout iteration.",
        )


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def terminate(iterable: Iterable[T], seconds: float) -> Iterator[T]:
    """Timeout iterator that raises TimeoutError when the timeout expires.

    Unlike `without_terminate`, this function forcibly raises TimeoutError
    after the specified number of seconds, even mid-iteration. It uses
    ``signal.SIGALRM`` / ``signal.setitimer()`` and is Unix-only.
    It cannot be used while another ITIMER_REAL timer is active.
    The timeout must be a positive finite number of seconds.

    Must be called from the main thread of the main interpreter.
    Calling from a worker thread raises ValueError.

    **Signal scope**: SIGALRM fires at any Python bytecode boundary in the
    calling thread, not only during fetches from the upstream iterable.
    The ``for`` loop body can also be interrupted and raise ``TimeoutError``.
    Keep loop body code interrupt-safe, or use ``without_terminate`` if the
    upstream must be fully consumed before yielding to the caller.
    """
    _require_main_thread()
    _ensure_itimer_real_is_available()
    validate_timeout_seconds(seconds)
    start = time.monotonic()
    end = start + seconds
    fired = False

    def handler(signum: int, _frame: object) -> None:
        nonlocal fired
        if fired or signum != signal.SIGALRM or time.monotonic() < end:
            return
        fired = True
        elapsed = time.monotonic() - start
        raise TimeoutError(
            f"timed out after {elapsed:.3f}s (limit: {seconds}s)",
        )

    original_handler = signal.signal(signal.SIGALRM, handler)
    try:
        signal.setitimer(signal.ITIMER_REAL, seconds)
        try:
            yield from iterable
        finally:
            signal.setitimer(signal.ITIMER_REAL, 0)
    finally:
        signal.signal(signal.SIGALRM, original_handler)
