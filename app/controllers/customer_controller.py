from flask import Blueprint, render_template
from sqlalchemy import text

from app.extensions import db
from app.repositories import MenuRepository, ReferenceRepository, UserRepository

customer_bp = Blueprint("customer", __name__)


@customer_bp.route("/")
def index():
    return render_template("index.html")


@customer_bp.route("/db-check")
def db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return "Подключение к PostgreSQL выполнено успешно"
    except Exception as error:
        return f"Ошибка подключения к базе данных: {error}", 500


@customer_bp.route("/data-check")
def data_check():
    try:
        menu_items = MenuRepository.get_available_menu()
        extras = MenuRepository.get_available_extras()
        order_types = ReferenceRepository.get_order_types()
        payment_methods = ReferenceRepository.get_payment_methods()
        demo_client = UserRepository.get_demo_client()

        return {
            "available_menu_count": len(menu_items),
            "available_extras_count": len(extras),
            "order_types": [item.name for item in order_types],
            "payment_methods": [item.name for item in payment_methods],
            "demo_client": demo_client.username if demo_client else None,
        }
    except Exception as error:
        return {
            "error": str(error)
        }, 500