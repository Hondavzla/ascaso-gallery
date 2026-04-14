from flask import Blueprint, abort, jsonify, request

from app.models.artist import Artist
from app.schemas.artist import ArtistSchema, ArtistSummarySchema

bp = Blueprint('artists', __name__, url_prefix='/api/artists')

summary_schema = ArtistSummarySchema(many=True)
detail_schema = ArtistSchema()


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
