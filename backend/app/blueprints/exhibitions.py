from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.exhibition import Exhibition
from app.schemas.exhibition import ExhibitionSchema
from app.services.auth import admin_required

bp = Blueprint('exhibitions', __name__, url_prefix='/api/exhibitions')

schema = ExhibitionSchema()
many_schema = ExhibitionSchema(many=True)
partial = ExhibitionSchema(partial=True)


@bp.get('')
def list_exhibitions():
    query = Exhibition.query
    status = request.args.get('status')
    if status:
        query = query.filter_by(status=status)
    query = query.order_by(Exhibition.display_order.asc(), Exhibition.id.asc())
    rows = query.all()
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_exhibition(slug):
    row = Exhibition.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    return jsonify(schema.dump(row))


@bp.post('')
@admin_required
def create_exhibition():
    data = schema.load(request.get_json() or {})
    row = Exhibition(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(schema.dump(row)), 201


@bp.put('/<slug>')
@admin_required
def update_exhibition(slug):
    row = Exhibition.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    data = partial.load(request.get_json() or {})
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return jsonify(schema.dump(row))


@bp.delete('/<slug>')
@admin_required
def delete_exhibition(slug):
    row = Exhibition.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return '', 204
