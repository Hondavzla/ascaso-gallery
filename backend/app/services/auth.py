import functools

from flask import abort, g
from flask_jwt_extended import jwt_required, get_jwt_identity
from passlib.hash import bcrypt

from app.models import AdminUser


def hash_password(plain: str) -> str:
    return bcrypt.using(rounds=12).hash(plain)


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.verify(plain, hashed)
    except ValueError:
        return False


def admin_required(fn):
    @functools.wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user_id = get_jwt_identity()
        user = AdminUser.query.get(user_id)
        if not user:
            abort(401)
        g.current_admin = user
        return fn(*args, **kwargs)
    return wrapper
