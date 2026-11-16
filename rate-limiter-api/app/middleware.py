from flask import current_app, request, jsonify
from app.limiter import FixedWindowLimiter


def exempt(view):
    """Mark a view so the rate limiter never blocks it."""
    view.rate_limit_exempt = True
    return view


def init_limiter(app, redis_client):
    limiter = FixedWindowLimiter(
        redis_client,
        max_requests=app.config["RATE_LIMIT"],
        window_seconds=app.config["RATE_WINDOW"],
    )

    @app.before_request
    def check_rate_limit():
        view = current_app.view_functions.get(request.endpoint)
        if getattr(view, "rate_limit_exempt", False):
            return None
        if not limiter.is_allowed(request.remote_addr):
            return jsonify({"error": "Rate Limit Exceeded"}), 429
