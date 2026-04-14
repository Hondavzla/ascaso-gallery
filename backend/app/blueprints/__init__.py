from app.blueprints.auth import bp as auth_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
