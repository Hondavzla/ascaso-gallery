from datetime import datetime

from flask import Blueprint, abort, jsonify, request

from app.extensions import db
from app.models.news import NewsArticle
from app.schemas.news import NewsArticleSchema
from app.services.auth import admin_required

bp = Blueprint('news', __name__, url_prefix='/api/news')

schema = NewsArticleSchema()
many_schema = NewsArticleSchema(many=True)
partial = NewsArticleSchema(partial=True)


def _is_drafts_request() -> bool:
    return request.args.get('drafts', '').lower() == 'true'


@bp.get('')
def list_news():
    if _is_drafts_request():
        # Admin-only path: delegate to a decorated helper so the main handler stays clean.
        return _list_news_admin()
    now = datetime.utcnow()
    rows = (
        NewsArticle.query
        .filter(NewsArticle.published_at.isnot(None))
        .filter(NewsArticle.published_at <= now)
        .order_by(NewsArticle.published_at.desc())
        .all()
    )
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@admin_required
def _list_news_admin():
    rows = NewsArticle.query.order_by(NewsArticle.created_at.desc()).all()
    return jsonify({'data': many_schema.dump(rows), 'count': len(rows)})


@bp.get('/<slug>')
def get_news(slug):
    row = NewsArticle.query.filter_by(slug=slug).first()
    if not row or row.published_at is None or row.published_at > datetime.utcnow():
        abort(404)
    return jsonify(schema.dump(row))


@bp.post('')
@admin_required
def create_news():
    data = schema.load(request.get_json() or {})
    row = NewsArticle(**data)
    db.session.add(row)
    db.session.commit()
    return jsonify(schema.dump(row)), 201


@bp.put('/<slug>')
@admin_required
def update_news(slug):
    row = NewsArticle.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    data = partial.load(request.get_json() or {})
    for key, value in data.items():
        setattr(row, key, value)
    db.session.commit()
    return jsonify(schema.dump(row))


@bp.delete('/<slug>')
@admin_required
def delete_news(slug):
    row = NewsArticle.query.filter_by(slug=slug).first()
    if not row:
        abort(404)
    db.session.delete(row)
    db.session.commit()
    return '', 204
