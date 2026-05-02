import asyncio
import functools
import sys

from playwright.async_api import Error as PlaywrightError


def with_retry(max_attempts: int = 3, base_delay: float = 1.0):
    """Playwright Error に対して指数バックオフリトライを付与するデコレータ。

    バックオフ: base_delay * 2^(attempt-1) → 1s, 2s, 4s
    ValueError 等のロジックエラーは即 re-raise。
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except PlaywrightError as e:
                    if attempt == max_attempts:
                        raise
                    delay = base_delay * (2 ** (attempt - 1))
                    print(
                        f"[retry {attempt}/{max_attempts - 1}] {delay}s: {e}",
                        file=sys.stderr,
                    )
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
