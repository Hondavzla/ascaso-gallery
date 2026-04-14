from datetime import datetime

from app.extensions import db


class ArtFair(db.Model):
    __tablename__ = 'art_fairs'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    dates = db.Column(db.String(200), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    booth = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
