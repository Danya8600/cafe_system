import hashlib

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

from app.repositories import UserRepository

auth_bp = Blueprint("auth", __name__)


def check_user_password(stored_hash: str, password: str) -> bool:
    """
    Поддерживает два варианта хранения пароля:
    1. старые демонстрационные пользователи из SQL-скрипта с md5;
    2. новые пользователи, зарегистрированные через приложение, с werkzeug-хэшем.
    """
    if not stored_hash:
        return False

    md5_hash = hashlib.md5(password.encode("utf-8")).hexdigest()

    if stored_hash == md5_hash:
        return True

    try:
        return check_password_hash(stored_hash, password)
    except ValueError:
        return False


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = UserRepository.get_by_username(username)

        if user is None or not check_user_password(user.password_hash, password):
            flash("Неверный логин или пароль.", "error")
            return redirect(url_for("auth.login"))

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role.name

        flash("Вы успешно вошли в систему.", "success")

        if user.role.name == "seller":
            return redirect(url_for("seller.show_new_orders"))

        return redirect(url_for("customer.show_menu"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        password_repeat = request.form.get("password_repeat", "")

        if not username or not password:
            flash("Введите логин и пароль.", "error")
            return redirect(url_for("auth.register"))

        if len(username) < 3:
            flash("Логин должен содержать минимум 3 символа.", "error")
            return redirect(url_for("auth.register"))

        if len(password) < 5:
            flash("Пароль должен содержать минимум 5 символов.", "error")
            return redirect(url_for("auth.register"))

        if password != password_repeat:
            flash("Пароли не совпадают.", "error")
            return redirect(url_for("auth.register"))

        existing_user = UserRepository.get_by_username(username)

        if existing_user is not None:
            flash("Пользователь с таким логином уже существует.", "error")
            return redirect(url_for("auth.register"))

        password_hash = generate_password_hash(password)
        user = UserRepository.create_client(username, password_hash)

        session["user_id"] = user.id
        session["username"] = user.username
        session["role"] = user.role.name

        flash("Регистрация выполнена успешно.", "success")
        return redirect(url_for("customer.show_menu"))

    return render_template("register.html")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Вы вышли из аккаунта.", "success")
    return redirect(url_for("customer.index"))
