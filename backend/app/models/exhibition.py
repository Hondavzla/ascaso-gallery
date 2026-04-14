from datetime import datetime

from app.extensions import db


class Exhibition(db.Model):
    __tablename__ = 'exhibitions'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    subtitle = db.Column(db.String(300), nullable=True)
    status = db.Column(db.String(20), nullable=False, index=True)  # 'current' | 'upcoming' | 'past'
    dates = db.Column(db.String(200), nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    description = db.Column(db.Text, nullable=True)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
