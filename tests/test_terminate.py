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
    # Do not timeout if the sent signal is not SIGALRM
    results = []
    for i in terminate(range(10), seconds=3.0):
        results.append(i)
        time.sleep(0.1)
        signal.alarm(signal.SIGWINCH)

    assert results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


def test_terminate_4() -> None:
    # Do not timeout if the signal sent but the time is longer than the timeout
    results = []
    for i in terminate(range(10), seconds=3.0):
        results.append(i)
        time.sleep(0.1)
        signal.alarm(signal.SIGALRM)

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


def test_nested_terminate_fails_fast_without_leaking_timer() -> None:
    original_handler = signal.getsignal(signal.SIGALRM)
    original_timer = signal.getitimer(signal.ITIMER_REAL)
    try:
        with pytest.raises(
            RuntimeError,
            match="ITIMER_REAL is already active",
        ):
            list(terminate(terminate(range(1), seconds=1.0), seconds=3.0))

        assert signal.getitimer(signal.ITIMER_REAL) == (0.0, 0.0)
        assert signal.getsignal(signal.SIGALRM) is original_handler
    finally:
        signal.setitimer(signal.ITIMER_REAL, *original_timer)
        signal.signal(signal.SIGALRM, original_handler)
