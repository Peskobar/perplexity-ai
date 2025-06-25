import asyncio
import functools
import random
from typing import Callable, Awaitable, TypeVar, ParamSpec

T = TypeVar('T')
P = ParamSpec('P')

def async_retry(max_retries: int = 3, base_delay: float = 1.0):
    """Dekorator do asynchronicznych funkcji, dodający logikę ponawiania prób z wykładniczym backoffem i jitterem."""
    def decorator(func: Callable[P, Awaitable[T]]) -> Callable[P, Awaitable[T]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            for i in range(max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    # packages.utils.src.logger by się przydał tutaj do logowania prób
                    # print(f"Próba {i+1}/{max_retries+1} nie powiodła się dla {func.__name__}: {e}")
                    if i == max_retries:
                        # print(f"Wszystkie {max_retries+1} próby dla {func.__name__} zakończone niepowodzeniem. Podnoszę wyjątek.")
                        raise e
                    # Oblicz opóźnienie: base_delay * (2 ** i) * (0.5 + random.random())
                    delay = base_delay * (2 ** i) * (0.5 + random.random() * 0.5) # Jitter między 0.5 a 1.0 * base_delay * 2^i
                    # print(f"Następna próba dla {func.__name__} za {delay:.2f}s...")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
