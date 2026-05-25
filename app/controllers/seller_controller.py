from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.extensions import db
from app.repositories import OrderRepository, ReferenceRepository, UserRepository

seller_bp = Blueprint("seller", __name__, url_prefix="/seller")


def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return UserRepository.get_by_id(user_id)


def seller_required():
    current_user = get_current_user()

    if current_user is None:
        flash("Для доступа к панели продавца необходимо войти в аккаунт.", "error")
        return None

    if current_user.role.name != "seller":
        flash("Раздел доступен только продавцу.", "error")
        return None

    return current_user


@seller_bp.route("/orders")
def show_orders():
    current_user = seller_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    status_filter = request.args.get("status", "new")

    if status_filter == "all":
        orders = OrderRepository.get_all_orders()
    else:
        orders = OrderRepository.get_orders_by_status(status_filter)

    statuses = ReferenceRepository.get_order_statuses()

    return render_template(
        "seller_orders.html",
        orders=orders,
        statuses=statuses,
        current_status=status_filter,
    )


@seller_bp.route("/orders/<int:order_id>")
def show_order_details(order_id):
    current_user = seller_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    order = OrderRepository.get_order_details(order_id)

    if order is None:
        flash("Заказ не найден.", "error")
        return redirect(url_for("seller.show_orders"))

    statuses = ReferenceRepository.get_order_statuses()

    return render_template(
        "seller_order_details.html",
        order=order,
        statuses=statuses,
    )


@seller_bp.route("/orders/<int:order_id>/accept", methods=["POST"])
def accept_order(order_id):
    current_user = seller_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    try:
        order = OrderRepository.get_by_id(order_id)

        if order is None:
            flash("Заказ не найден.", "error")
            return redirect(url_for("seller.show_orders"))

        if order.status.name != "new":
            flash("Принять можно только новый заказ.", "error")
            return redirect(url_for("seller.show_order_details", order_id=order_id))

        OrderRepository.accept_order(order_id=order_id, seller_id=current_user.id)
        flash("Заказ успешно принят.", "success")
        return redirect(url_for("seller.show_order_details", order_id=order_id))

    except Exception as error:
        db.session.rollback()
        flash(f"Ошибка при принятии заказа: {error}", "error")
        return redirect(url_for("seller.show_order_details", order_id=order_id))


@seller_bp.route("/orders/<int:order_id>/status", methods=["POST"])
def update_order_status(order_id):
    current_user = seller_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    try:
        status_id = request.form.get("status_id", type=int)
        status = ReferenceRepository.get_status_by_id(status_id)

        if status is None:
            flash("Выбран некорректный статус заказа.", "error")
            return redirect(url_for("seller.show_order_details", order_id=order_id))

        order = OrderRepository.get_by_id(order_id)

        if order is None:
            flash("Заказ не найден.", "error")
            return redirect(url_for("seller.show_orders"))

        if order.accepted_by_id is None:
            flash("Перед изменением статуса заказ необходимо принять.", "error")
            return redirect(url_for("seller.show_order_details", order_id=order_id))

        OrderRepository.update_status(order_id=order_id, status_id=status.id)
        flash("Статус заказа обновлён.", "success")
        return redirect(url_for("seller.show_order_details", order_id=order_id))

    except Exception as error:
        db.session.rollback()
        flash(f"Ошибка при обновлении статуса: {error}", "error")
        return redirect(url_for("seller.show_order_details", order_id=order_id))
