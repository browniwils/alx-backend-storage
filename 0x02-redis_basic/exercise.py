#!/usr/bin/env python3
"""Redis NoSQL data storage module."""

import redis
import uuid
from functools import wraps
from typing import Any
from typing import Callable
from typing import Union


def count_calls(method: Callable) -> Callable:
    """Tracks the number of calls made to a method in a Cache class."""

    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """Get and returns the given method after
        incrementing its call counter."""

        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)

    return wrapper


def call_history(method: Callable) -> Callable:
    """Keeps the call details of a method in a Cache class."""

    @wraps(method)
    def invoker(self, *args, **kwargs) -> Any:
        """Get an returns the method's output
        after storing its inputs and output."""

        in_key = f"{method.__qualname__}:inputs"
        out_key = f"{method.__qualname__}:outputs"
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return invoker


def replay(fn: Callable) -> None:
    """Show call history of a Cache class method."""

    if fn is None or not hasattr(fn, "__self__"):
        return
    redis_store = getattr(fn.__self__, "_redis", None)
    if not isinstance(redis_store, redis.Redis):
        return
    fxn_name = fn.__qualname__
    in_key = f"{fxn_name}:inputs"
    out_key = f"{fxn_name}:outputs"
    fxn_call_count = 0

    if redis_store.exists(fxn_name) != 0:
        fxn_call_count = int(redis_store.get(fxn_name))
    print('{} was called {} times:'.format(fxn_name, fxn_call_count))
    fxn_inputs = redis_store.lrange(in_key, 0, -1)
    fxn_outputs = redis_store.lrange(out_key, 0, -1)
    for fxn_input, fxn_output in zip(fxn_inputs, fxn_outputs):
        utf8_ = "utf-8"
        print(f"{fxn_name}(*{fxn_input.decode(utf8_)}) -> {fxn_output}")


class Cache:
    """Object for storing data in a Redis data storage."""

    def __init__(self) -> None:
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data:  Union[str, bytes, int, float]) -> str:
        """Persist a value in a Redis data storage and returns the key."""

        dk = str(uuid.uuid4())
        self._redis.set(dk, data)
        return dk

    def get(
            self,
            key: str,
            fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        """Retrieves a value from a Redis data storage."""

        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_str(self, key: str) -> str:
        """Get string value from a Redis data storage."""

        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieves an integer value from a Redis data storage."""

        return self.get(key, lambda x: int(x))
