from flask import Flask

from app.config import CONFIG_MAP
from app.errors import register_error_handlers
from app.extensions import db, migrate, jwt, cors, limiter


def create_app(config_name: str = 'prod') -> Flask:
    app = Flask(__name__)
    app.config.from_object(CONFIG_MAP[config_name])

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    cors.init_app(
        app,
        resources={r'/api/*': {'origins': app.config['CORS_ORIGINS'] or '*'}},
        supports_credentials=True,
    )
    limiter.init_app(app)

    register_error_handlers(app)

    @app.get('/api/health')
    def health():
        return {'status': 'ok'}

    return app
