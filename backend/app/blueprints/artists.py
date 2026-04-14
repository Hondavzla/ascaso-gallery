from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.artist import Artist
from app.schemas.artist import ArtistSchema, ArtistSummarySchema
from app.services.auth import admin_required

bp = Blueprint('artists', __name__, url_prefix='/api/artists')

summary_schema = ArtistSummarySchema(many=True)
detail_schema = ArtistSchema()
load_schema = ArtistSchema()
partial_schema = ArtistSchema(partial=True)


@bp.get('')
def list_artists():
    query = Artist.query
    if request.args.get('featured', '').lower() == 'true':
        query = query.filter_by(featured=True)
    query = query.order_by(Artist.display_order.asc(), Artist.name.asc())
    rows = query.all()
    return jsonify({'data': summary_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    return jsonify(detail_schema.dump(artist))


@bp.post('')
@admin_required
def create_artist():
    data = load_schema.load(request.get_json() or {})
    artist = Artist(**data)
    db.session.add(artist)
    db.session.commit()
    return jsonify(detail_schema.dump(artist)), 201


@bp.put('/<slug>')
@admin_required
def update_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    data = partial_schema.load(request.get_json() or {})
    for key, value in data.items():
        setattr(artist, key, value)
    db.session.commit()
    return jsonify(detail_schema.dump(artist))


@bp.delete('/<slug>')
@admin_required
def delete_artist(slug):
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    db.session.delete(artist)
    db.session.commit()
    return '', 204


from app.models.artist import ArtWork
from app.schemas.artist import ArtWorkSchema

artwork_schema = ArtWorkSchema()
artwork_partial_schema = ArtWorkSchema(partial=True)


def _get_artist_or_404(slug: str) -> Artist:
    artist = Artist.query.filter_by(slug=slug).first()
    if not artist:
        abort(404)
    return artist


@bp.post('/<slug>/artworks')
@admin_required
def create_artwork(slug):
    artist = _get_artist_or_404(slug)
    data = artwork_schema.load(request.get_json() or {})
    work = ArtWork(artist_id=artist.id, **data)
    db.session.add(work)
    db.session.commit()
    return jsonify(artwork_schema.dump(work)), 201


@bp.put('/<slug>/artworks/<work_slug>')
@admin_required
def update_artwork(slug, work_slug):
    artist = _get_artist_or_404(slug)
    work = ArtWork.query.filter_by(artist_id=artist.id, slug=work_slug).first()
    if not work:
        abort(404)
    data = artwork_partial_schema.load(request.get_json() or {})
    for key, value in data.items():
        setattr(work, key, value)
    db.session.commit()
    return jsonify(artwork_schema.dump(work))


@bp.delete('/<slug>/artworks/<work_slug>')
@admin_required
def delete_artwork(slug, work_slug):
    artist = _get_artist_or_404(slug)
    work = ArtWork.query.filter_by(artist_id=artist.id, slug=work_slug).first()
    if not work:
        abort(404)
    db.session.delete(work)
    db.session.commit()
    return '', 204
