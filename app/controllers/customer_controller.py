from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from sqlalchemy import text

from app.extensions import db
from app.patterns import DishBuilder, OrderFactory, OrderLine, PaymentContext, PaymentStrategyFactory
from app.repositories import (
    MenuRepository,
    OrderRepository,
    ReferenceRepository,
    UserRepository,
)

customer_bp = Blueprint("customer", __name__)

PICKUP_ADDRESS = "г. Ярославль, ул. Центральная, д. 5, точка выдачи Cafe Order"


def get_current_user():
    user_id = session.get("user_id")

    if user_id is None:
        return None

    return UserRepository.get_by_id(user_id)


def login_required():
    user = get_current_user()

    if user is None:
        flash("Для выполнения действия необходимо войти в аккаунт.", "error")
        return None

    return user


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

        return {
            "available_menu_count": len(menu_items),
            "available_extras_count": len(extras),
            "order_types": [item.name for item in order_types],
            "payment_methods": [item.name for item in payment_methods],
            "current_user": session.get("username"),
        }
    except Exception as error:
        return {
            "error": str(error)
        }, 500


@customer_bp.route("/menu")
def show_menu():
    current_user = login_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    if current_user.role.name != "client":
        flash("Оформлять заказы может только клиент.", "error")
        return redirect(url_for("customer.index"))

    menu_items = MenuRepository.get_available_menu()
    extras = MenuRepository.get_available_extras()
    order_types = ReferenceRepository.get_order_types()
    payment_methods = ReferenceRepository.get_payment_methods()

    return render_template(
        "customer_menu.html",
        menu_items=menu_items,
        extras=extras,
        order_types=order_types,
        payment_methods=payment_methods,
        pickup_address=PICKUP_ADDRESS
    )


@customer_bp.route("/orders/create", methods=["POST"])
def create_order():
    try:
        current_user = login_required()

        if current_user is None:
            return redirect(url_for("auth.login"))

        if current_user.role.name != "client":
            flash("Оформлять заказы может только клиент.", "error")
            return redirect(url_for("customer.index"))

        selected_item_ids = request.form.getlist("menu_item_ids")

        if not selected_item_ids:
            flash("Выберите хотя бы одно блюдо.", "error")
            return redirect(url_for("customer.show_menu"))

        order_type_id = request.form.get("order_type_id", type=int)
        payment_method_id = request.form.get("payment_method_id", type=int)
        delivery_address = request.form.get("address", "").strip()

        order_type = ReferenceRepository.get_order_type_by_id(order_type_id)
        payment_method = ReferenceRepository.get_payment_method_by_id(payment_method_id)

        if order_type is None:
            flash("Выберите тип заказа.", "error")
            return redirect(url_for("customer.show_menu"))

        if payment_method is None:
            flash("Выберите способ оплаты.", "error")
            return redirect(url_for("customer.show_menu"))

        if order_type.name == "delivery":
            if not delivery_address:
                flash("Для доставки необходимо указать адрес.", "error")
                return redirect(url_for("customer.show_menu"))

            order_address = delivery_address
        else:
            order_address = PICKUP_ADDRESS

        order_lines = []

        for item_id_raw in selected_item_ids:
            if not item_id_raw.isdigit():
                continue

            item_id = int(item_id_raw)
            menu_item = MenuRepository.get_item_by_id(item_id)

            if menu_item is None or not menu_item.is_available:
                flash("Одно из выбранных блюд недоступно.", "error")
                return redirect(url_for("customer.show_menu"))

            quantity = request.form.get(f"quantity_{item_id}", type=int)

            if quantity is None or quantity < 1:
                flash("Количество блюда должно быть не меньше 1.", "error")
                return redirect(url_for("customer.show_menu"))

            extra_ids_raw = request.form.getlist(f"extra_ids_{item_id}")
            extra_ids = [int(extra_id) for extra_id in extra_ids_raw if extra_id.isdigit()]
            extras = MenuRepository.get_extras_by_ids(extra_ids)

            dish = DishBuilder.build(menu_item, extras)

            order_lines.append(
                OrderLine(
                    menu_item=menu_item,
                    dish=dish,
                    extras=extras,
                    quantity=quantity
                )
            )

        if not order_lines:
            flash("Не удалось сформировать состав заказа.", "error")
            return redirect(url_for("customer.show_menu"))

        order = OrderFactory.create_order(order_type, order_lines, order_address, payment_method)

        payment_context = PaymentContext()
        payment_strategy = PaymentStrategyFactory.create_strategy(payment_method)
        payment_context.set_strategy(payment_strategy)

        payment_result = payment_context.execute_payment(order.calculate_total())

        if not payment_result.is_success():
            flash(payment_result.get_message(), "error")
            return redirect(url_for("customer.show_menu"))

        order_record = OrderRepository.save_order(
            order=order,
            customer_id=current_user.id
        )

        flash(payment_result.get_message(), "success")
        return redirect(url_for("customer.order_result", order_id=order_record.id))

    except Exception as error:
        db.session.rollback()
        flash(f"Ошибка при создании заказа: {error}", "error")
        return redirect(url_for("customer.show_menu"))


@customer_bp.route("/orders/<int:order_id>/result")
def order_result(order_id):
    current_user = login_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    order = OrderRepository.get_by_id(order_id)

    if order is None:
        flash("Заказ не найден.", "error")
        return redirect(url_for("customer.show_menu"))

    if order.customer_id != current_user.id:
        flash("Вы не можете просматривать чужой заказ.", "error")
        return redirect(url_for("customer.my_orders"))

    return render_template("customer_result.html", order=order)


@customer_bp.route("/orders/my")
def my_orders():
    current_user = login_required()

    if current_user is None:
        return redirect(url_for("auth.login"))

    if current_user.role.name != "client":
        flash("Раздел доступен только клиенту.", "error")
        return redirect(url_for("customer.index"))

    orders = OrderRepository.get_customer_orders(current_user.id)

    return render_template("customer_orders.html", orders=orders)