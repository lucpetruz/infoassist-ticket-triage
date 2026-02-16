from flask import Flask
from dotenv import load_dotenv

from app.extensions import db, migrate
from app.config import Config
from .routes_predict import predict_bp
from .routes_ui import ui_bp

def create_app():
    load_dotenv(override=False)

    app = Flask(__name__)
    app.config.from_object(Config)

    # init estensioni
    db.init_app(app)
    migrate.init_app(app, db)

    # health check
    @app.get("/health")
    def health():
        return {"status": "ok"}

    # blueprint
    app.register_blueprint(predict_bp)
    app.register_blueprint(ui_bp)

    return app


