import time
from collections.abc import Callable


def wait_until(
    condition: Callable[[], bool],
    timeout: float = 60,
    interval: float = 1,
    message: str = "condition",
    ignore: tuple[type[Exception], ...] = (),
) -> None:
    """Poll ``condition`` until it succeeds or the timeout expires.

    Exceptions listed in ``ignore`` are treated as a condition that is not ready yet.
    """
    deadline = time.monotonic() + timeout
    last_error = None
    while True:
        try:
            if condition():
                return
        except ignore as error:
            last_error = error
        if time.monotonic() >= deadline:
            detail = f" (last error: {last_error})" if last_error else ""
            raise TimeoutError(f"Timed out after {timeout}s waiting for {message}{detail}")
        time.sleep(interval)
