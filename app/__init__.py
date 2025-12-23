from flask import Flask, current_app
from .config import Config
from .extensions import db, migrate, login_manager


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @app.context_processor
    def inject_turnstile_key():
        return {
            "TURNSTILE_SITE_KEY": current_app.config.get("TURNSTILE_SITE_KEY")
        }


    from . import routes, models, auth_routes, bookmarks, deals
    # Register blueprints or routes
    app.register_blueprint(routes.main_bp)
    app.register_blueprint(auth_routes.auth_bp)
    app.register_blueprint(bookmarks.bp)
    app.register_blueprint(deals.deal_bp)


    return app