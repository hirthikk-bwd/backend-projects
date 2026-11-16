import math
import time
import uuid


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
    def is_allowed(self, identifier):
        now = time.time()
        key = f"rate_limit:swlog:{identifier}"
        # Unique member so concurrent requests with the same timestamp all count
        member = f"{now}:{uuid.uuid4().hex}"
        pipe = self.redis.pipeline()
        pipe.zremrangebyscore(key, 0, now - self.window_seconds)
        pipe.zadd(key, {member: now})
        pipe.zcard(key)
        pipe.expire(key, self.window_seconds)
        _, _, count, _ = pipe.execute()
        if count > self.max_requests:
            # Don't let rejected requests occupy space in the window
            self.redis.zrem(key, member)
            return False
        return True


class SlidingWindowCounterLimiter(WindowLimiter):
    def is_allowed(self, identifier):
        now = time.time()
        current_window = int(now) // self.window_seconds
        current_key = f"rate_limit:swcount:{identifier}:{current_window}"
        prev_key = f"rate_limit:swcount:{identifier}:{current_window - 1}"
        # Claim a slot first (INCR is atomic), then undo it if over the limit
        pipe = self.redis.pipeline()
        pipe.incr(current_key)
        pipe.expire(current_key, self.window_seconds * 2)
        pipe.get(prev_key)
        current_count, _, prev_count = pipe.execute()
        elapsed_in_window = (now % self.window_seconds) / self.window_seconds
        weighted_count = int(prev_count or 0) * (1 - elapsed_in_window)
        if weighted_count + current_count - 1 >= self.max_requests:
            self.redis.decr(current_key)
            return False
        return True


# Refill and take a token in a single atomic step, so concurrent requests
# can't both spend the last token.
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


class TokenBucketLimiter:
    def __init__(self, redis_client, max_tokens, refill_rate):
        self.max = max_tokens
        self.refill_rate = refill_rate  # tokens per second
        # Once the bucket would be full again the state is redundant; let it expire
        self.ttl = math.ceil(max_tokens / refill_rate) + 1
        self._script = redis_client.register_script(TOKEN_BUCKET_SCRIPT)

    def is_allowed(self, identifier):
        key = f"rate_limit:token:{identifier}"
        args = [self.max, self.refill_rate, time.time(), self.ttl]
        return self._script(keys=[key], args=args) == 1
