from flask import Flask


def create_app():
    app = Flask(__name__)

    from app.controllers.customer_controller import customer_bp
    app.register_blueprint(customer_bp)

    return app