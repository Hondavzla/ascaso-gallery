from datetime import datetime

from flask import Blueprint, jsonify, request, g
from flask_jwt_extended import create_access_token
from marshmallow import ValidationError

from app.extensions import db, limiter
from app.models import AdminUser
from app.schemas.auth import LoginSchema, AdminUserSchema
from app.services.auth import verify_password, admin_required

bp = Blueprint('auth', __name__, url_prefix='/api/auth')

login_schema = LoginSchema()
user_schema = AdminUserSchema()


@bp.post('/login')
@limiter.limit('5 per minute')
def login():
    try:
        data = login_schema.load(request.get_json() or {})
    except ValidationError:
        raise
    user = AdminUser.query.filter_by(email=data['email']).first()
    if not user or not verify_password(data['password'], user.password_hash):
        from flask import abort
        abort(401)
    user.last_login_at = datetime.utcnow()
    db.session.commit()
    token = create_access_token(identity=str(user.id))
    return jsonify({'access_token': token, 'user': user_schema.dump(user)})


@bp.get('/me')
@admin_required
def me():
    return jsonify(user_schema.dump(g.current_admin))
