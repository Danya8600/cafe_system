from flask import Blueprint, render_template, request, redirect, url_for, flash
from sqlalchemy import text

from app.extensions import db
from app.patterns import DishBuilder, OrderFactory, PaymentContext, PaymentStrategyFactory
from app.repositories import (
    MenuRepository,
    ReferenceRepository,
    UserRepository,
    OrderRepository,
)

customer_bp = Blueprint("customer", __name__)

PICKUP_ADDRESS = "г. Ярославль, ул. Центральная, д. 5, точка выдачи Cafe Order"


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


@customer_bp.route("/menu")
def show_menu():
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
        demo_client = UserRepository.get_demo_client()

        if demo_client is None:
            flash("В базе данных не найден демонстрационный клиент client1.", "error")
            return redirect(url_for("customer.show_menu"))

        menu_item_id = request.form.get("menu_item_id", type=int)
        order_type_id = request.form.get("order_type_id", type=int)
        payment_method_id = request.form.get("payment_method_id", type=int)
        delivery_address = request.form.get("address", "").strip()
        extra_ids = request.form.getlist("extra_ids")

        extra_ids = [int(extra_id) for extra_id in extra_ids if extra_id.isdigit()]

        menu_item = MenuRepository.get_item_by_id(menu_item_id)
        order_type = ReferenceRepository.get_order_type_by_id(order_type_id)
        payment_method = ReferenceRepository.get_payment_method_by_id(payment_method_id)
        extras = MenuRepository.get_extras_by_ids(extra_ids)

        if menu_item is None or not menu_item.is_available:
            flash("Выбранное блюдо недоступно.", "error")
            return redirect(url_for("customer.show_menu"))

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

        dish = DishBuilder.build(menu_item, extras)
        order = OrderFactory.create_order(order_type, dish, order_address, payment_method)

        payment_context = PaymentContext()
        payment_strategy = PaymentStrategyFactory.create_strategy(payment_method)
        payment_context.set_strategy(payment_strategy)

        payment_result = payment_context.execute_payment(order.calculate_total())

        if not payment_result.is_success():
            flash(payment_result.get_message(), "error")
            return redirect(url_for("customer.show_menu"))

        order_record = OrderRepository.save_order(
            order=order,
            customer_id=demo_client.id,
            menu_item=menu_item,
            extras=extras
        )

        flash(payment_result.get_message(), "success")
        return redirect(url_for("customer.order_result", order_id=order_record.id))

    except Exception as error:
        db.session.rollback()
        flash(f"Ошибка при создании заказа: {error}", "error")
        return redirect(url_for("customer.show_menu"))


@customer_bp.route("/orders/<int:order_id>/result")
def order_result(order_id):
    order = OrderRepository.get_by_id(order_id)

    if order is None:
        flash("Заказ не найден.", "error")
        return redirect(url_for("customer.show_menu"))

    return render_template("customer_result.html", order=order)


@customer_bp.route("/orders/my")
def my_orders():
    demo_client = UserRepository.get_demo_client()

    if demo_client is None:
        flash("В базе данных не найден демонстрационный клиент client1.", "error")
        return redirect(url_for("customer.index"))

    orders = OrderRepository.get_customer_orders(demo_client.id)

    return render_template("customer_orders.html", orders=orders)