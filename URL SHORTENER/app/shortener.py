import random
import string
from app import db
from app.models import URL

ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

def encode(number):
    result = ""
    while number > 0:
        remainder = number % 62
        result = ALPHABET[remainder] + result
        number = number // 62
    return result

def generate_short_code(original_url):
    url_entry = URL(
        short_code = "temp",
        original_url=original_url
    )
    db.session.add(url_entry)
    db.session.flush()

    short_code = encode(url_entry.id)

    url_entry.short_code =  short_code
    db.session.commit()

    return short_code
