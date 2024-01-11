# python-timeout-iterator

## Usage

### without_terminate

`without_terminate` is a generator that it will not yield after the timeout,
but it will not raise an exception.

```python
from timeout_iterator import without_terminate
results = []
for i in without_terminate(range(10), seconds=0.3):
    results.append(i)
    time.sleep(0.1)

assert results == [0, 1, 2]
```

### terminate

`terminate` is a generator that it will raise an exception after the timeout.

```python
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

# LICENSE

BSD 3-Clause License
