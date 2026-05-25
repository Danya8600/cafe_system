from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import (
    OrderItemExtraRecord,
    OrderItemRecord,
    OrderRecord,
)
from app.repositories.reference_repository import ReferenceRepository


class OrderRepository:
    @staticmethod
    def save_order(order, customer_id):
        new_status = ReferenceRepository.get_status_by_name("new")

        if new_status is None:
            raise ValueError("В базе данных не найден статус заказа 'new'.")

        order_record = OrderRecord(
            customer_id=customer_id,
            accepted_by_id=None,
            order_type_id=order.order_type.id,
            payment_method_id=order.payment_method.id,
            status_id=new_status.id,
            total_price=Decimal(order.calculate_total()),
            address=order.address,
            created_at=datetime.now(),
            accepted_at=None,
        )

        db.session.add(order_record)
        db.session.flush()

        for line in order.order_lines:
            order_item = OrderItemRecord(
                order_id=order_record.id,
                menu_item_id=line.menu_item.id,
                quantity=line.quantity,
                base_price=Decimal(line.menu_item.price),
            )

            db.session.add(order_item)
            db.session.flush()

            for extra in line.extras:
                order_item_extra = OrderItemExtraRecord(
                    order_item_id=order_item.id,
                    extra_id=extra.id,
                    extra_price=Decimal(extra.price),
                )
                db.session.add(order_item_extra)

        db.session.commit()

        return order_record

    @staticmethod
    def get_by_id(order_id):
        return OrderRecord.query.get(order_id)

    @staticmethod
    def get_customer_orders(customer_id):
        return (
            OrderRecord.query
            .filter_by(customer_id=customer_id)
            .order_by(OrderRecord.created_at.desc())
            .all()
        )

    @staticmethod
    def get_all_orders():
        return (
            OrderRecord.query
            .options(
                joinedload(OrderRecord.customer),
                joinedload(OrderRecord.accepted_by),
                joinedload(OrderRecord.order_type),
                joinedload(OrderRecord.payment_method),
                joinedload(OrderRecord.status),
            )
            .order_by(OrderRecord.created_at.desc())
            .all()
        )

    @staticmethod
    def get_orders_by_status(status_name):
        status = ReferenceRepository.get_status_by_name(status_name)

        if status is None:
            return []

        return (
            OrderRecord.query
            .options(
                joinedload(OrderRecord.customer),
                joinedload(OrderRecord.accepted_by),
                joinedload(OrderRecord.order_type),
                joinedload(OrderRecord.payment_method),
                joinedload(OrderRecord.status),
            )
            .filter(OrderRecord.status_id == status.id)
            .order_by(OrderRecord.created_at.desc())
            .all()
        )

    @staticmethod
    def get_new_orders():
        return OrderRepository.get_orders_by_status("new")

    @staticmethod
    def get_order_details(order_id):
        return (
            OrderRecord.query
            .options(
                joinedload(OrderRecord.customer),
                joinedload(OrderRecord.accepted_by),
                joinedload(OrderRecord.order_type),
                joinedload(OrderRecord.payment_method),
                joinedload(OrderRecord.status),
                joinedload(OrderRecord.items)
                .joinedload(OrderItemRecord.menu_item),
                joinedload(OrderRecord.items)
                .joinedload(OrderItemRecord.extras)
                .joinedload(OrderItemExtraRecord.extra),
            )
            .filter(OrderRecord.id == order_id)
            .first()
        )

    @staticmethod
    def accept_order(order_id, seller_id):
        accepted_status = ReferenceRepository.get_status_by_name("accepted")

        if accepted_status is None:
            raise ValueError("В базе данных не найден статус заказа 'accepted'.")

        order = OrderRepository.get_by_id(order_id)

        if order is None:
            raise ValueError("Заказ не найден.")

        order.accepted_by_id = seller_id
        order.status_id = accepted_status.id
        order.accepted_at = datetime.now()

        db.session.commit()

        return order

    @staticmethod
    def update_status(order_id, status_id):
        order = OrderRepository.get_by_id(order_id)

        if order is None:
            raise ValueError("Заказ не найден.")

        order.status_id = status_id
        db.session.commit()

        return order
