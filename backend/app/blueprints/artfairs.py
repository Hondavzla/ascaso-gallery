from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.artfair import ArtFair
from app.schemas.artfair import ArtFairSchema
from app.services.auth import admin_required

bp = Blueprint('artfairs', __name__, url_prefix='/api/artfairs')

schema = ArtFairSchema()
many_schema = ArtFairSchema(many=True)
partial = ArtFairSchema(partial=True)


@bp.get('')
def list_artfairs():
    query = ArtFair.query
    year = request.args.get('year')
    if year:
        query = query.filter_by(year=int(year))
    query = query.order_by(ArtFair.year.desc(), ArtFair.name.asc())
    rows = query.all()
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@bp.get('/latest')
def latest_artfair():
    row = ArtFair.query.order_by(ArtFair.year.desc(), ArtFair.id.desc()).first()
    if not row:
        abort(404)
    return jsonify(schema.dump(row))


@bp.get('/<slug>')
def get_artfair(slug):
    row = ArtFair.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    return jsonify(schema.dump(row))


@bp.post('')
@admin_required
def create_artfair():
    data = schema.load(request.get_json() or {})
    row = ArtFair(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(schema.dump(row)), 201


@bp.put('/<slug>')
@admin_required
def update_artfair(slug):
    row = ArtFair.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    data = partial.load(request.get_json() or {})
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return jsonify(schema.dump(row))


@bp.delete('/<slug>')
@admin_required
def delete_artfair(slug):
    row = ArtFair.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return '', 204
