from flask import Flask

from .extensions import db


def create_app(config_override: dict | None = None) -> Flask:
    """Application factory for the Flask project."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )

    app.config.from_object("app.config.Config")

    if config_override:
        app.config.update(config_override)

    db.init_app(app)

    from .routes import bp as main_blueprint  # pylint: disable=import-outside-toplevel
    from .api import api as api_blueprint  # pylint: disable=import-outside-toplevel

    app.register_blueprint(main_blueprint)
    app.register_blueprint(api_blueprint)

    @app.context_processor
    def inject_globals():
        from datetime import datetime
        from flask import current_app

        return {
            "current_year": datetime.utcnow().year,
            "telegram_support_url": current_app.config.get("TELEGRAM_SUPPORT_URL"),
        }

    with app.app_context():
        from . import data  # pylint: disable=import-outside-toplevel

        db.create_all()
        data.ensure_seed_data()

    return app
