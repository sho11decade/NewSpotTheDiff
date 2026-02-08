"""Flask routes package."""

from flask import Flask


def register_blueprints(app: Flask) -> None:
    from src.routes.main import bp as main_bp
    from src.routes.upload import bp as upload_bp
    from src.routes.generate import bp as generate_bp
    from src.routes.pages import bp as pages_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(upload_bp)
    app.register_blueprint(generate_bp)
    app.register_blueprint(pages_bp)
