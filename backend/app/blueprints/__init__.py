from app.blueprints.auth import bp as auth_bp
from app.blueprints.artists import bp as artists_bp
from app.blueprints.exhibitions import bp as exhibitions_bp
from app.blueprints.news import bp as news_bp
from app.blueprints.artfairs import bp as artfairs_bp


def register_blueprints(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(artists_bp)
    app.register_blueprint(exhibitions_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(artfairs_bp)
