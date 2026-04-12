from flask import Blueprint, request, jsonify, redirect
from app import db
from app.models import URL
from app.shortener import generate_short_code
from app.cache import get_cached_url, set_cached_url

bp = Blueprint('urls', __name__)

@bp.route('/shorten', methods = ['POST'])
def shorten_url():
    data = request.get_json()
    if not data or 'url' not in data:
        return jsonify({'error': 'URL is required'}), 400
    
    original_url = data['url']
    short_code = generate_short_code(original_url)
    set_cached_url(short_code, original_url)

    return jsonify({
        'short_code': short_code,
        'short_url': f"/{short_code}",
        'original_url': original_url
    }), 201

@bp.route('/<code>')
def redirect_url(code):
    cached = get_cached_url(code)
    if cached:
        return redirect(cached, code=302)
    url_entry = URL.query.filter_by(short_code=code).first()
    if not url_entry:
        return jsonify({'error': 'URL not found'}), 404
    
    url_entry.clicks += 1
    db.session.commit()
    set_cached_url(code, url_entry.original_url)

    return redirect(url_entry.original_url, code = 302)

@bp.route('/stats/<code>')
def get_stats(code):
    url_entry = URL.query.filter_by(short_code=code).first()
    if not url_entry:
        return jsonify({'error': 'URL not found'}), 404
    
    return jsonify(url_entry.to_dict()), 200

