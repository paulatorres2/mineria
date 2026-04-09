from flask import Flask, render_template

from config import Config, DevelopmentConfig


def create_app(config_class: type[Config] = DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import main_bp
    app.register_blueprint(main_bp)

    _register_error_handlers(app)

    return app


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(404)
    def not_found(error) -> tuple[str, int]:
        return render_template("404.html"), 404

    @app.errorhandler(500)
    def internal_error(error) -> tuple[str, int]:
        app.logger.error("Server error: %s", error)
        return render_template("500.html"), 500
