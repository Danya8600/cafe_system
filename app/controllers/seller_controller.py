from flask import Blueprint, flash, redirect, render_template, session, url_for

from app.repositories import OrderRepository, UserRepository

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")


def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return UserRepository.get_by_id(user_id)


def get_current_seller_or_redirect():
    current_user = get_current_user()

    if current_user is None:
        flash("Для доступа к панели продавца необходимо войти в аккаунт.", "error")
        return None, redirect(url_for("auth.login"))

    if current_user.role.name != "seller":
        flash("Панель продавца доступна только пользователям с ролью продавца.", "error")
        return None, redirect(url_for("customer.index"))

    return current_user, None


@seller_bp.route("/orders")
def show_new_orders():
    current_seller, redirect_response = get_current_seller_or_redirect()

    if redirect_response is not None:
        return redirect_response

    orders = OrderRepository.get_new_orders()

    return render_template(
        "seller_orders.html",
        orders=orders,
        current_seller=current_seller
    )


@seller_bp.route("/orders/<int:order_id>")
def show_order_details(order_id):
    current_seller, redirect_response = get_current_seller_or_redirect()

    if redirect_response is not None:
        return redirect_response

    order = OrderRepository.get_order_details(order_id)

    if order is None:
        flash("Заказ не найден.", "error")
        return redirect(url_for("seller.show_new_orders"))

    return render_template(
        "seller_order_details.html",
        order=order,
        current_seller=current_seller
    )
