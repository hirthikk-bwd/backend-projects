import time
import redis
from flask import current_app


def get_redis():
    return redis.Redis(
        host=current_app.config["REDIS_HOST"],
        port=current_app.config["REDIS_PORT"],
        db=0,
        decode_responses=True,
    )


class FixedWindowLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, identifier):
        r = get_redis()
        window = int(time.time()) // self.window_seconds
        key = f"rate_limit:fixed:{identifier}:{window}"
        count = r.incr(key)
        if count == 1:
            r.expire(key, self.window_seconds)
        return count <= self.max_requests


class SlidingWindowLogLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, identifier):
        r = get_redis()
        now = time.time()
        window_start = now - self.window_seconds
        key = f"rate_limit:swlog:{identifier}"
        r.zremrangebyscore(key, 0, window_start)
        r.zadd(key, {str(now): now})
        r.expire(key, self.window_seconds)
        count = r.zcount(key, window_start, now)
        return count <= self.max_requests


class TokenBucketLimiter:
    def __init__(self, max_tokens, refill_rate):
        self.max = max_tokens
        self.refill_rate = refill_rate  # tokens per second

    def is_allowed(self, identifier):
        r = get_redis()
        now = time.time()
        key_tokens = f"rate_limit:token:{identifier}:tokens"
        key_time = f"rate_limit:token:{identifier}:last_time"

        tokens = r.get(key_tokens)
        last_time = r.get(key_time)

        if tokens is None or last_time is None:
            r.set(key_tokens, self.max - 1)
            r.set(key_time, now)
            return True

        elapsed = now - float(last_time)
        new_tokens = min(self.max, float(tokens) + elapsed * self.refill_rate)

        if new_tokens < 1:
            return False

        r.set(key_tokens, new_tokens - 1)
        r.set(key_time, now)
        return True


class SlidingWindowCounterLimiter:
    def __init__(self, max_requests, window_seconds):
        self.max_requests = max_requests
        self.window_seconds = window_seconds

    def is_allowed(self, identifier):
        r = get_redis()
        now = time.time()
        current_window = int(now) // self.window_seconds
        prev_window = current_window - 1
        current_key = f"rate_limit:swcount:{identifier}:{current_window}"
        prev_key = f"rate_limit:swcount:{identifier}:{prev_window}"
        current_count = int(r.get(current_key) or 0)
        prev_count = int(r.get(prev_key) or 0)
        elapsed_in_window = (now % self.window_seconds) / self.window_seconds
        weighted_count = prev_count * (1 - elapsed_in_window) + current_count
        if weighted_count >= self.max_requests:
            return False
        r.incr(current_key)
        r.expire(current_key, self.window_seconds * 2)
        return True
