from flask import Flask

from app.config import Config
from app.extensions import db


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    from app.controllers.auth_controller import auth_bp
    from app.controllers.customer_controller import customer_bp
    from app.controllers.seller_controller import seller_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(customer_bp)
    app.register_blueprint(seller_bp)

    return app
