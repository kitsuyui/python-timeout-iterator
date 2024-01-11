from collections.abc import Iterable
import datetime


def without_terminate(iterable: Iterable, seconds: float | int) -> Iterable:
    """Timeout iterator

    This iterator times out after the specified number of seconds.
    This iterator cannot forcibly terminate a running task.
    It just ends without executing the next task.
    """
    now = datetime.datetime.now()
    end = now + datetime.timedelta(seconds=seconds)
    for item in iterable:
        if datetime.datetime.now() > end:
            break
        yield item
