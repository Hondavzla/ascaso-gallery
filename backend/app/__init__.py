from flask import Flask

from app.blueprints import register_blueprints
from app.config import CONFIG_MAP
from app.errors import register_error_handlers
from app.extensions import db, migrate, jwt, cors, limiter


def create_app(config_name: str = 'prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)
    from app import models as _models  # noqa: F401  -- register models with SQLAlchemy metadata
    migrate.init_app(app, db)
    jwt.init_app(app)

    from flask import jsonify, g

    def _unauth(reason: str):
        return jsonify({
            'error': {
                'code': 'unauthorized',
                'message': 'Authentication required',
                'request_id': getattr(g, 'request_id', None),
            }
        }), 401

    @jwt.unauthorized_loader
    def _jwt_unauthorized(reason):
        return _unauth(reason)

    @jwt.invalid_token_loader
    def _jwt_invalid(reason):
        return _unauth(reason)

    @jwt.expired_token_loader
    def _jwt_expired(header, payload):
        return _unauth('expired')

    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'] or '*'}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    register_error_handlers(app)
    register_blueprints(app)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    return app
