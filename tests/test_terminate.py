import os
import signal
import time
from collections.abc import Callable

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


def test_terminate_error_has_message() -> None:
    # TimeoutError should include the configured limit in its message.
    with pytest.raises(TimeoutError) as exc_info:
        for _i in terminate(range(100), seconds=0.1):
            time.sleep(0.05)
    assert str(exc_info.value) != ""
    assert "0.1s" in str(exc_info.value)


def test_terminate_handler_not_reentrant(  # noqa: C901
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    # Capture terminate()'s SIGALRM handler and call it a second time to verify
    # the fired flag makes re-entrant delivery a no-op.
    captured: list[Callable[[int, object], None]] = []
    real_fn = signal.signal

    def spy(signum: int, h: signal.Handlers) -> signal.Handlers:
        r = real_fn(signum, h)
        if signum == signal.SIGALRM and callable(h):
            captured.append(h)
        return r  # type: ignore[return-value]

    monkeypatch.setattr(signal, "signal", spy)
    with pytest.raises(TimeoutError):
        for _i in terminate(range(100), seconds=0.1):
            time.sleep(0.05)

    assert len(captured) == 1
    # Without fired flag this would raise a second TimeoutError (end is past).
    captured[0](signal.SIGALRM, None)


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


@pytest.mark.parametrize(
    "seconds",
    [0, -0.1, float("inf"), float("-inf"), float("nan")],
)
def test_terminate_rejects_invalid_seconds_without_signal_changes(
    seconds: float,
) -> None:
    original_handler = signal.getsignal(signal.SIGALRM)
    original_timer = signal.getitimer(signal.ITIMER_REAL)
    try:
        with pytest.raises(ValueError, match="positive finite"):
            list(terminate(range(1), seconds=seconds))

        assert signal.getsignal(signal.SIGALRM) == original_handler
        assert signal.getitimer(signal.ITIMER_REAL) == original_timer
    finally:
        signal.setitimer(signal.ITIMER_REAL, *original_timer)
        signal.signal(signal.SIGALRM, original_handler)
