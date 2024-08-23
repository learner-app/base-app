import time
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import Config

db = SQLAlchemy()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)

    from src.endpoints import users_bp, products_bp

    app.register_blueprint(users_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")

    @app.route("/api/time")
    def get_current_time():
        return {"time": time.time()}

    return app
