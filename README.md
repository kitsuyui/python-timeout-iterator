# python-timeout-iterator

`timeout-iterator` provides a timeout in iteration.

[![Python](https://img.shields.io/pypi/pyversions/timeout-iterator.svg)](https://badge.fury.io/py/timeout-iterator)
[![PyPI version](https://img.shields.io/pypi/v/timeout-iterator.svg)](https://pypi.python.org/pypi/timeout-iterator/)
![Coverage](https://raw.githubusercontent.com/kitsuyui/octocov-central/main/badges/kitsuyui/python-timeout-iterator/coverage.svg)
[![License](https://img.shields.io/badge/License-BSD%203--Clause-blue.svg)](https://opensource.org/licenses/BSD-3-Clause)

## Installation

```bash
$ pip install timeout-iterator
```

## Usage

### without_terminate

`without_terminate` stops yielding items once the timeout elapses without
raising an exception. It is safe to use on all platforms because it does not
use signals.

```python
import time

from timeout_iterator import without_terminate
results = []
for i in without_terminate(range(10), seconds=0.3):
    results.append(i)
    time.sleep(0.1)

assert results == [0, 1, 2]
```

**Boundary behavior**: The timeout is checked *after* each item is fetched
from the upstream iterator. If the deadline passes between a fetch and its
yield, the fetched item is silently dropped. At most one item near the
boundary may be consumed from the upstream but not passed to the caller.
This differs from `terminate`, which delivers every item fetched before the
SIGALRM fires.

### terminate

`terminate` is a generator that it will raise an exception after the timeout.
This function uses `signal.SIGALRM` and `signal.setitimer()`, so it is only
supported on Unix-like platforms that provide those signal APIs.

```python
import time

from timeout_iterator import terminate
try:
    results = []
    for i in terminate(range(10), seconds=0.3):
        results.append(i)
        time.sleep(0.1)
except TimeoutError:
    pass

assert results == [0, 1, 2]
```

**Signal scope**: `SIGALRM` is delivered at any Python bytecode boundary in
the calling thread — not only during fetches from the upstream iterator.  The
loop body itself can be interrupted and raise `TimeoutError`.  Keep loop body
code safe to interrupt at any point, or use `without_terminate` if you need the
upstream items to be fully consumed before yielding control.

# LICENSE

BSD 3-Clause License
