from dataclasses import dataclass
import logging
import time

@dataclass(kw_only=True)
class BaseConfig:
    name: str
    emoji: str = "🧩"

    def __str__(self):
        return f"{self.emoji}{self.name}"

def timer(func, logger: str) -> callable:
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        elapsed_time: float = (end - start)
        if elapsed_time > 1:
            logging.getLogger(logger).debug(f"{logger}.{func.__name__} took ⏳ {elapsed_time:.2f}s")
        else:
            logging.getLogger(logger).debug(f"{logger}.{func.__name__} took ⏳ {elapsed_time * 1000:.2f}ms")
        return result
    return wrapper

def async_timer(func, logger: str) -> callable:
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        end = time.time()
        elapsed_time: float = (end - start)
        if elapsed_time > 1:
            logging.getLogger(logger).debug(f"{logger}.{func.__name__} took ⏳ {elapsed_time:.2f}s")
        else:
            logging.getLogger(logger).debug(f"{logger}.{func.__name__} took ⏳ {elapsed_time * 1000:.2f}ms")
        return result
    return wrapper