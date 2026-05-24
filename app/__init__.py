from flask import Flask

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.controllers.customer_controller import customer_bp
    app.register_blueprint(customer_bp)

    return app