import time

import pytest

from timeout_iterator import terminate


def test_terminate() -> None:
    # If the time is shorter than the timeout, it will time out with a TimeoutError.
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
