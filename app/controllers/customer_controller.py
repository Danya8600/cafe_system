from flask import Blueprint, render_template
from sqlalchemy import text

from app.extensions import db

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