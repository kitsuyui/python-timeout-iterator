import math


def validate_timeout_seconds(seconds: float) -> None:
    if seconds > 0 and math.isfinite(seconds):
        return

    message = "seconds must be a positive finite number"
    raise ValueError(message)
