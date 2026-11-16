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


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


@pytest.fixture
def client(fake_redis):
    app = create_app(
        config_overrides={"TESTING": True, "RATE_LIMIT": 2, "RATE_WINDOW": 60},
        redis_client=fake_redis,
    )
    return app.test_client()


@pytest.mark.parametrize("limiter_cls", WINDOW_LIMITERS)
def test_window_limiter_blocks_after_limit(fake_redis, limiter_cls):
    limiter = limiter_cls(fake_redis, max_requests=3, window_seconds=60)
    assert limiter.is_allowed("test_user")
    assert limiter.is_allowed("test_user")
    assert limiter.is_allowed("test_user")
    assert not limiter.is_allowed("test_user")


@pytest.mark.parametrize("limiter_cls", WINDOW_LIMITERS)
def test_window_limiter_tracks_users_separately(fake_redis, limiter_cls):
    limiter = limiter_cls(fake_redis, max_requests=2, window_seconds=60)
    assert limiter.is_allowed("user_a")
    assert limiter.is_allowed("user_b")
    assert limiter.is_allowed("user_a")
    assert not limiter.is_allowed("user_a")
    assert limiter.is_allowed("user_b")


def test_window_keys_expire(fake_redis):
    FixedWindowLimiter(fake_redis, max_requests=3, window_seconds=60).is_allowed("u")
    SlidingWindowLogLimiter(fake_redis, max_requests=3, window_seconds=60).is_allowed(
        "u"
    )
    for key in fake_redis.keys("rate_limit:*"):
        assert 0 < fake_redis.ttl(key) <= 120


def test_sliding_log_does_not_record_rejected_requests(fake_redis):
    limiter = SlidingWindowLogLimiter(fake_redis, max_requests=2, window_seconds=60)
    for _ in range(5):
        limiter.is_allowed("u")
    assert fake_redis.zcard("rate_limit:swlog:u") == 2


def test_token_bucket_allows_burst_then_refills(fake_redis, monkeypatch):
    now = [1000.0]
    monkeypatch.setattr("app.limiter.time.time", lambda: now[0])
    limiter = TokenBucketLimiter(fake_redis, max_tokens=3, refill_rate=1)

    assert limiter.is_allowed("u")
    assert limiter.is_allowed("u")
    assert limiter.is_allowed("u")
    assert not limiter.is_allowed("u")

    now[0] += 1  # one token refilled
    assert limiter.is_allowed("u")
    assert not limiter.is_allowed("u")
    assert 0 < fake_redis.ttl("rate_limit:token:u") <= limiter.ttl


def test_middleware_uses_configured_limit(client):
    assert client.get("/limited").status_code == 200
    assert client.get("/limited").status_code == 200
    response = client.get("/limited")
    assert response.status_code == 429
    assert response.get_json() == {"error": "Rate Limit Exceeded"}


def test_exempt_route_is_never_blocked(client):
    for _ in range(5):
        assert client.get("/unlimited").status_code == 200
