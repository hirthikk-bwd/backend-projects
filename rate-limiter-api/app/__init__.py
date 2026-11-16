import redis
from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix
from app.config import Config


def create_app(config_overrides=None, redis_client=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config_overrides:
        app.config.update(config_overrides)

    # Only trust X-Forwarded-For when a known number of proxies sits in front;
    # otherwise clients could spoof their IP to dodge the limiter.
    if app.config["TRUSTED_PROXIES"]:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=app.config["TRUSTED_PROXIES"])

    # One client per app: its connection pool is reused across requests
    if redis_client is None:
        redis_client = redis.Redis(
            host=app.config["REDIS_HOST"],
            port=app.config["REDIS_PORT"],
            db=0,
            decode_responses=True,
        )

    from app.routes import bp

    app.register_blueprint(bp)

    from app.middleware import init_limiter

    init_limiter(app, redis_client)

    return app
