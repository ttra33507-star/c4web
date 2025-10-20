from flask import Flask


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

    from .routes import bp as main_blueprint  # pylint: disable=import-outside-toplevel

    app.register_blueprint(main_blueprint)

    @app.context_processor
    def inject_globals():
        from datetime import datetime

        return {
            "current_year": datetime.utcnow().year,
        }

    return app
