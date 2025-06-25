import os
import sys
import importlib.util
import pytest

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

async_retry_path = os.path.join(ROOT_DIR, 'packages', 'utils', 'src', 'async_retry.py')
spec = importlib.util.spec_from_file_location('async_retry', async_retry_path)
async_retry_mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(async_retry_mod)
async_retry = async_retry_mod.async_retry


async def succeed_after_attempts(n, fail_times):
    """Helper coroutine that fails `fail_times` times then returns."""
    for _ in range(fail_times):
        raise ValueError("fail")
    return n


@pytest.mark.asyncio
async def test_async_retry_success(monkeypatch):
    attempts = 0

    async def func():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise RuntimeError("boom")
        return "ok"

    wrapped = async_retry(max_retries=4, base_delay=0)(func)
    result = await wrapped()
    assert result == "ok"
    assert attempts == 3

@pytest.mark.asyncio
async def test_async_retry_exhaust(monkeypatch):
    attempts = 0

    async def func():
        nonlocal attempts
        attempts += 1
        raise RuntimeError("boom")

    wrapped = async_retry(max_retries=2, base_delay=0)(func)
    with pytest.raises(RuntimeError):
        await wrapped()
    assert attempts == 3
