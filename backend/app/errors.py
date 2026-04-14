import logging
import uuid
from typing import Optional

from flask import g, jsonify, request
from marshmallow import ValidationError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import (
    NotFound,
    Unauthorized,
    Forbidden,
    RequestEntityTooLarge,
    UnsupportedMediaType,
    HTTPException,
)

logger = logging.getLogger(__name__)


def _envelope(code: str, message: str, status: int, details: Optional[dict] = None):
    payload = {
        'error': {
            'code': code,
            'message': message,
            'request_id': getattr(g, 'request_id', None),
        }
    }
    if details is not None:
        payload['error']['details'] = details
    return jsonify(payload), status


def register_error_handlers(app):
    @app.before_request
    def _attach_request_id():
        g.request_id = uuid.uuid4().hex

    @app.errorhandler(ValidationError)
    def handle_validation(err):
        return _envelope('validation_error', 'Request body failed validation', 422, err.messages)

    @app.errorhandler(NotFound)
    def handle_not_found(err):
        return _envelope('not_found', 'Resource not found', 404)

    @app.errorhandler(Unauthorized)
    def handle_unauthorized(err):
        return _envelope('unauthorized', 'Authentication required', 401)

    @app.errorhandler(Forbidden)
    def handle_forbidden(err):
        return _envelope('forbidden', 'You do not have permission', 403)

    @app.errorhandler(RequestEntityTooLarge)
    def handle_too_large(err):
        return _envelope('file_too_large', 'Uploaded file exceeds size limit', 413)

    @app.errorhandler(UnsupportedMediaType)
    def handle_bad_media(err):
        return _envelope('unsupported_media_type', 'Unsupported media type', 415)

    @app.errorhandler(IntegrityError)
    def handle_integrity(err):
        from app.extensions import db
        db.session.rollback()
        return _envelope('conflict', 'Resource already exists or violates a constraint', 409)

    @app.errorhandler(HTTPException)
    def handle_http(err):
        return _envelope(err.name.lower().replace(' ', '_'), err.description or err.name, err.code or 500)

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        logger.exception('unhandled exception on %s %s', request.method, request.path)
        return _envelope('internal_error', 'An unexpected error occurred', 500)
