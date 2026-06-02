import time
from collections.abc import Iterator

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


class CloseableIterator(Iterator[int]):
    def __init__(self, values: list[int]) -> None:
        self.closed = False
        self._values = iter(values)

    def __next__(self) -> int:
        return next(self._values)

    def close(self) -> None:
        self.closed = True


def test_without_terminate_closes_upstream_on_timeout() -> None:
    upstream = CloseableIterator([0, 1])

    results = []
    for i in without_terminate(upstream, seconds=0.01):
        results.append(i)
        time.sleep(0.02)

    assert results == [0]
    assert upstream.closed


def test_without_terminate_does_not_close_upstream_on_completion() -> None:
    upstream = CloseableIterator([0])

    assert list(without_terminate(upstream, seconds=3.0)) == [0]
    assert not upstream.closed
