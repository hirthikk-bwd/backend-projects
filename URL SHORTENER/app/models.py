from datetime import datetime
from app import db


class URL(db.Model):
    __tablename__ = 'urls'

    id = db.Column(db.Integer, primary_key=True)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    original_url = db.Column(db.Text, nullable=False)
    clicks = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    def to_dict(self):
        return {
            'short_code': self.short_code,
            'original_url': self.original_url,
            'clicks': self.clicks,
            'created_at': self.created_at.isoformat()
        }
    