import os
import signal
import time

import pytest

from timeout_iterator import terminate


def test_terminate() -> None:
    # A short timeout raises TimeoutError before the loop finishes.
    results = []
    with pytest.raises(TimeoutError):
        for i in terminate(range(10), seconds=0.3):
            results.append(i)
            time.sleep(0.1)

    assert results == [0, 1, 2]


def test_terminate_2() -> None:
    # If the time is longer than the timeout, it will complete normally.
    results = []
    for i in terminate(range(10), seconds=3.0):
        results.append(i)
        time.sleep(0.1)

    assert results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_terminate_3() -> None:
    # Do not timeout if the sent signal is not SIGALRM.
    # Use os.kill to actually deliver SIGWINCH (not signal.alarm, which
    # schedules SIGALRM after N seconds using the signal number as a duration).
    results = []
    for i in terminate(range(10), seconds=3.0):
        results.append(i)
        time.sleep(0.1)
        os.kill(os.getpid(), signal.SIGWINCH)

    assert results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_terminate_4() -> None:
    # Do not timeout if SIGALRM fires but the deadline has not been reached.
    # Use os.kill to actually deliver SIGALRM, exercising the
    # `datetime.datetime.now() < end` guard in the handler.
    results = []
    for i in terminate(range(10), seconds=3.0):
        results.append(i)
        time.sleep(0.1)
        os.kill(os.getpid(), signal.SIGALRM)

    assert results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_terminate_restores_sigalrm_handler() -> None:
    def handler(signum: int, _frame: object) -> None:
        raise AssertionError(f"unexpected signal: {signum}")

    original_handler = signal.getsignal(signal.SIGALRM)
    signal.signal(signal.SIGALRM, handler)
    try:
        list(terminate(range(1), seconds=3.0))

        assert signal.getsignal(signal.SIGALRM) is handler
    finally:
        signal.signal(signal.SIGALRM, original_handler)
