import types

import pytest
import fakeredis
from app import create_app
from app.limiter import (
    FixedWindowLimiter,
    SlidingWindowCounterLimiter,
    SlidingWindowLogLimiter,
    TokenBucketLimiter,
)

WINDOW_LIMITERS = [
    FixedWindowLimiter,
    SlidingWindowLogLimiter,
    SlidingWindowCounterLimiter,
]


class FakeClock:
    """Controls the limiter's view of time without touching global time.time."""

    def __init__(self, now):
        self.now = now

    def advance(self, seconds):
        self.now += seconds


@pytest.fixture
def clock(monkeypatch):
    # 20s into a 60s window, so tests never straddle a window boundary
    fake = FakeClock(1_000_020.0)
    fake_time = types.SimpleNamespace(time=lambda: fake.now)
    monkeypatch.setattr("app.limiter.time", fake_time)
    return fake


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def client(fake_redis, clock):
    app = create_app(
        config_overrides={"TESTING": True, "RATE_LIMIT": 2, "RATE_WINDOW": 60},
        redis_client=fake_redis,
    )
    return app.test_client()


@pytest.mark.parametrize("limiter_cls", WINDOW_LIMITERS)
def test_window_limiter_blocks_after_limit(fake_redis, clock, limiter_cls):
    limiter = limiter_cls(fake_redis, max_requests=3, window_seconds=60)
    assert limiter.is_allowed("test_user")
    assert limiter.is_allowed("test_user")
    assert limiter.is_allowed("test_user")
    assert not limiter.is_allowed("test_user")


@pytest.mark.parametrize("limiter_cls", WINDOW_LIMITERS)
def test_window_limiter_tracks_users_separately(fake_redis, clock, limiter_cls):
    limiter = limiter_cls(fake_redis, max_requests=2, window_seconds=60)
    assert limiter.is_allowed("user_a")
    assert limiter.is_allowed("user_b")
    assert limiter.is_allowed("user_a")
    assert not limiter.is_allowed("user_a")
    assert limiter.is_allowed("user_b")


@pytest.mark.parametrize("limiter_cls", WINDOW_LIMITERS)
def test_window_limiter_allows_again_after_window(fake_redis, clock, limiter_cls):
    limiter = limiter_cls(fake_redis, max_requests=1, window_seconds=60)
    assert limiter.is_allowed("u")
    assert not limiter.is_allowed("u")
    clock.advance(120)
    assert limiter.is_allowed("u")


@pytest.mark.parametrize("limiter_cls", WINDOW_LIMITERS)
def test_window_keys_expire(fake_redis, clock, limiter_cls):
    limiter_cls(fake_redis, max_requests=3, window_seconds=60).is_allowed("u")
    keys = fake_redis.keys("rate_limit:*")
    assert keys
    for key in keys:
        assert 0 < fake_redis.ttl(key) <= 120


def test_sliding_log_does_not_record_rejected_requests(fake_redis, clock):
    limiter = SlidingWindowLogLimiter(fake_redis, max_requests=2, window_seconds=60)
    for _ in range(5):
        limiter.is_allowed("u")
    assert fake_redis.zcard("rate_limit:swlog:u") == 2


def test_sliding_counter_does_not_count_rejected_requests(fake_redis, clock):
    limiter = SlidingWindowCounterLimiter(
        fake_redis, max_requests=2, window_seconds=60
    )
    for _ in range(5):
        limiter.is_allowed("u")
    (key,) = fake_redis.keys("rate_limit:swcount:*")
    assert fake_redis.get(key) == "2"


def test_sliding_counter_keys_share_cluster_slot(fake_redis, clock):
    limiter = SlidingWindowCounterLimiter(
        fake_redis, max_requests=5, window_seconds=60
    )
    limiter.is_allowed("u")
    clock.advance(60)
    limiter.is_allowed("u")
    keys = fake_redis.keys("rate_limit:swcount:*")
    assert len(keys) == 2
    assert all("{u}" in key for key in keys)


def test_token_bucket_allows_burst_then_refills(fake_redis, clock):
    limiter = TokenBucketLimiter(fake_redis, max_tokens=3, refill_rate=1)

    assert limiter.is_allowed("u")
    assert limiter.is_allowed("u")
    assert limiter.is_allowed("u")
    assert not limiter.is_allowed("u")

    clock.advance(1)  # one token refilled
    assert limiter.is_allowed("u")
    assert not limiter.is_allowed("u")
    assert 0 < fake_redis.ttl("rate_limit:token:u") <= limiter.ttl


def test_token_bucket_rejects_non_positive_refill_rate(fake_redis):
    with pytest.raises(ValueError):
        TokenBucketLimiter(fake_redis, max_tokens=3, refill_rate=0)


def test_middleware_uses_configured_limit(client):
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    response = client.get("/limited")
    assert response.status_code == 429
    assert response.get_json() == {"error": "Rate Limit Exceeded"}


def test_exempt_route_is_never_blocked(client):
    for _ in range(5):
        assert client.get("/unlimited").status_code == 200
