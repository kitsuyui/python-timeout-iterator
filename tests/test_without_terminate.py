import time

import pytest

from timeout_iterator import without_terminate


def test_without_terminate_1() -> None:
    # If the time is shorter than the timeout, it will time out normally.
    results = []
    for i in without_terminate(range(10), seconds=0.3):
        results.append(i)
        time.sleep(0.1)

    assert results == [0, 1, 2]


def test_without_terminate_2() -> None:
    # If the time is longer than the timeout, it will complete normally.
    results = []
    for i in without_terminate(range(10), seconds=3.0):
        results.append(i)
        time.sleep(0.1)

    assert results == [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]


@pytest.mark.parametrize(
    "seconds",
    [0, -0.1, float("inf"), float("-inf"), float("nan")],
)
def test_without_terminate_rejects_invalid_seconds(seconds: float) -> None:
    with pytest.raises(ValueError, match="positive finite"):
        list(without_terminate(range(1), seconds=seconds))
