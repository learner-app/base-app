from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config
import os

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from src.endpoints.users import users_bp
    from src.endpoints.decks import decks_bp
    from src.endpoints.terms import terms_bp
    from src.endpoints.prompts import prompts_bp

    app.register_blueprint(users_bp, url_prefix="/")
    app.register_blueprint(decks_bp, url_prefix="/")
    app.register_blueprint(terms_bp, url_prefix="/")
    app.register_blueprint(prompts_bp, url_prefix="/")

    return app
