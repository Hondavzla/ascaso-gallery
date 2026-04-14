from datetime import datetime

from sqlalchemy import UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON

from app.extensions import db


# JSONB on Postgres, JSON (text) on SQLite. Marshmallow sees both as dict/list.
JSONType = JSON().with_variant(JSONB(), 'postgresql')


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String(120), unique=True, nullable=False, index=True)
    name = db.Column(db.String(200), nullable=False)
    medium = db.Column(db.String(100), nullable=True)
    nationality = db.Column(db.String(100), nullable=True)
    eyebrow = db.Column(db.String(100), nullable=True)
    hero_image_url = db.Column(db.String(500), nullable=True)
    featured = db.Column(db.Boolean, default=False, nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)

    bio = db.Column(JSONType, nullable=True)
    quote = db.Column(JSONType, nullable=True)
    awards = db.Column(JSONType, nullable=True)
    collections = db.Column(JSONType, nullable=True)
    exhibitions_history = db.Column(JSONType, nullable=True)
    monumental_works = db.Column(JSONType, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    works = db.relationship(
        'ArtWork',
        back_populates='artist',
        cascade='all, delete-orphan',
        order_by='ArtWork.display_order',
    )


class ArtWork(db.Model):
    __tablename__ = 'artworks'
    __table_args__ = (UniqueConstraint('artist_id', 'slug', name='uq_artwork_artist_slug'),)

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id', ondelete='CASCADE'), nullable=False, index=True)
    slug = db.Column(db.String(120), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    year = db.Column(db.Integer, nullable=True)
    medium = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(500), nullable=False)
    display_order = db.Column(db.Integer, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    artist = db.relationship('Artist', back_populates='works')
