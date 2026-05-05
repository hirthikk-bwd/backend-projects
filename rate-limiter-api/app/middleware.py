from flask import request, jsonify
from app.limiter import FixedWindowLimiter

limiter = FixedWindowLimiter(max_requests=5, window_seconds=60)


def init_limiter(app):
    @app.before_request
    def check_rate_limit():
        if request.path == "/unlimited":
            return None
        identifier = request.remote_addr
        if not limiter.is_allowed(identifier):
            return jsonify({"error": "Rate Limit Exceeded"}), 429
