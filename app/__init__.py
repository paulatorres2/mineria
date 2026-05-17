from flask import Flask, render_template

from config import Config, DevelopmentConfig


def create_app(config_class: type[Config] = DevelopmentConfig) -> Flask:
    app = Flask(__name__)
    app.config.from_object(config_class)

    from app.main import main_bp
    from app.nivel_1 import nivel_1_bp
    from app.nivel_2 import nivel_2_bp
    from app.nivel_3 import nivel_3_bp
    from app.nivel_4 import nivel_4_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(nivel_1_bp)
    app.register_blueprint(nivel_2_bp)
    app.register_blueprint(nivel_3_bp)
    app.register_blueprint(nivel_4_bp)

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
