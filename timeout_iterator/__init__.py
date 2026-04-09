from timeout_iterator.terminate import terminate
from timeout_iterator.without_terminate import without_terminate

# https://packaging-guide.openastronomy.org/en/latest/advanced/versioning.html
from ._version import __version__

__all__ = ["__version__", "terminate", "without_terminate"]
