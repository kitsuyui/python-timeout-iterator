from collections.abc import Iterable
import datetime
import signal


# NOTE: float type accepts int
# https://peps.python.org/pep-0484/#the-numeric-tower
def terminate(iterable: Iterable, seconds: float) -> Iterable:
    """Timeout iterator

    This iterator forcibly terminates a running task after the specified number of seconds.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)

    def handler(signum: int, frame: object) -> None:
        if signum != signal.SIGALRM:
            return
        if datetime.datetime.now() < end:
            return
        raise TimeoutError

    signal.signal(signal.SIGALRM, handler)
    signal.setitimer(signal.ITIMER_REAL, seconds)

    try:
        for item in iterable:
            yield item
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
