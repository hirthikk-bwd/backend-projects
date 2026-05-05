import pytest
import fakeredis
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def fake_redis():
    return fakeredis.FakeRedis(decode_responses=True)


def test_fixed_window_allows_requests(app, fake_redis, monkeypatch):
    monkeypatch.setattr("app.limiter.get_redis", lambda: fake_redis)
    from app.limiter import FixedWindowLimiter

    limiter = FixedWindowLimiter(max_requests=3, window_seconds=60)
    with app.app_context():
        assert limiter.is_allowed("test_user") == True
        assert limiter.is_allowed("test_user") == True
        assert limiter.is_allowed("test_user") == True
        assert limiter.is_allowed("test_user") == False


def test_fixed_window_different_users(app, fake_redis, monkeypatch):
    monkeypatch.setattr("app.limiter.get_redis", lambda: fake_redis)
    from app.limiter import FixedWindowLimiter

    limiter = FixedWindowLimiter(max_requests=2, window_seconds=60)
    with app.app_context():
        assert limiter.is_allowed("user_a") == True
        assert limiter.is_allowed("user_b") == True
        assert limiter.is_allowed("user_a") == True
        assert limiter.is_allowed("user_a") == False
        assert limiter.is_allowed("user_b") == True
