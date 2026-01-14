from flask import Flask
from dotenv import load_dotenv
import os

def create_app():
    load_dotenv()

    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")
    app.config["DATABASE_URL"] = os.getenv("DATABASE_URL")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app
