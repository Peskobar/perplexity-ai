import functools
import random
import time
from typing import Callable, TypeVar, ParamSpec

T = TypeVar('T')
P = ParamSpec('P')


def retry(max_retries: int = 3, base_delay: float = 1.0) -> Callable[[Callable[P, T]], Callable[P, T]]:
    """Simple retry decorator with exponential backoff."""
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if i == max_retries:
                        raise
                    delay = base_delay * (2 ** i) * (0.5 + random.random() * 0.5)
                    time.sleep(delay)
        return wrapper
    return decorator
