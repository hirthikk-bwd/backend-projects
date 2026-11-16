import math
import time
import uuid

# Each check that must read state before writing it runs as a Lua script, so
# it is atomic in Redis and costs a single round trip.

SLIDING_LOG_SCRIPT = """
local now = tonumber(ARGV[1])
local window = tonumber(ARGV[2])
redis.call("ZREMRANGEBYSCORE", KEYS[1], 0, now - window)
if redis.call("ZCARD", KEYS[1]) >= tonumber(ARGV[3]) then
    return 0
end
redis.call("ZADD", KEYS[1], now, ARGV[4])
redis.call("EXPIRE", KEYS[1], window)
return 1
"""

SLIDING_COUNTER_SCRIPT = """
local current = tonumber(redis.call("GET", KEYS[1]) or "0")
local prev = tonumber(redis.call("GET", KEYS[2]) or "0")
if prev * tonumber(ARGV[2]) + current >= tonumber(ARGV[1]) then
    return 0
end
redis.call("INCR", KEYS[1])
redis.call("EXPIRE", KEYS[1], ARGV[3])
return 1
"""

TOKEN_BUCKET_SCRIPT = """
local max_tokens = tonumber(ARGV[1])
local refill_rate = tonumber(ARGV[2])
local now = tonumber(ARGV[3])
local state = redis.call("HMGET", KEYS[1], "tokens", "last_time")
local tokens = tonumber(state[1]) or max_tokens
local last_time = tonumber(state[2]) or now
tokens = math.min(max_tokens, tokens + (now - last_time) * refill_rate)
local allowed = 0
if tokens >= 1 then
    tokens = tokens - 1
    allowed = 1
end
redis.call("HSET", KEYS[1], "tokens", tokens, "last_time", now)
redis.call("EXPIRE", KEYS[1], ARGV[4])
return allowed
"""


class WindowLimiter:
    """Shared setup for limiters configured as N requests per window."""

    def __init__(self, redis_client, max_requests, window_seconds):
        self.redis = redis_client
        self.max_requests = max_requests
        self.window_seconds = window_seconds


class FixedWindowLimiter(WindowLimiter):
    def is_allowed(self, identifier):
        window = int(time.time()) // self.window_seconds
        key = f"rate_limit:fixed:{identifier}:{window}"
        # INCR + EXPIRE in one round trip, applied atomically (MULTI/EXEC)
        pipe = self.redis.pipeline()
        pipe.incr(key)
        pipe.expire(key, self.window_seconds)
        count, _ = pipe.execute()
        return count <= self.max_requests


class SlidingWindowLogLimiter(WindowLimiter):
    def __init__(self, redis_client, max_requests, window_seconds):
        super().__init__(redis_client, max_requests, window_seconds)
        self._script = redis_client.register_script(SLIDING_LOG_SCRIPT)

    def is_allowed(self, identifier):
        now = time.time()
        # Unique member so concurrent requests with the same timestamp all count
        member = f"{now}:{uuid.uuid4().hex}"
        args = [now, self.window_seconds, self.max_requests, member]
        return self._script(keys=[f"rate_limit:swlog:{identifier}"], args=args) == 1


class SlidingWindowCounterLimiter(WindowLimiter):
    def __init__(self, redis_client, max_requests, window_seconds):
        super().__init__(redis_client, max_requests, window_seconds)
        self._script = redis_client.register_script(SLIDING_COUNTER_SCRIPT)

    def is_allowed(self, identifier):
        now = time.time()
        current_window = int(now) // self.window_seconds
        # {identifier} hash tag keeps both keys in one Redis Cluster slot
        prefix = f"rate_limit:swcount:{{{identifier}}}"
        keys = [f"{prefix}:{current_window}", f"{prefix}:{current_window - 1}"]
        prev_weight = 1 - (now % self.window_seconds) / self.window_seconds
        args = [self.max_requests, prev_weight, self.window_seconds * 2]
        return self._script(keys=keys, args=args) == 1


class TokenBucketLimiter:
    def __init__(self, redis_client, max_tokens, refill_rate):
        if refill_rate <= 0:
            raise ValueError("refill_rate must be positive (tokens per second)")
        self.max = max_tokens
        self.refill_rate = refill_rate  # tokens per second
        # Once the bucket would be full again the state is redundant; let it expire
        self.ttl = math.ceil(max_tokens / refill_rate) + 1
        self._script = redis_client.register_script(TOKEN_BUCKET_SCRIPT)

    def is_allowed(self, identifier):
        key = f"rate_limit:token:{identifier}"
        args = [self.max, self.refill_rate, time.time(), self.ttl]
        return self._script(keys=[key], args=args) == 1
