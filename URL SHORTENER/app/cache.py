from flask import current_app


def get_cached_url(short_code):
    key = f"url:{short_code}"
    cached = current_app.redis.get(key)
    if cached:
        return cached
    return None

def set_cached_url(short_code, original_url, ttl=3600):
    key = f"url:{short_code}"
    current_app.redis.setex(key, ttl, original_url)

def delete_cached_url(short_code):
    key = f"url:{short_code}"
    current_app.redis.delete(key)
