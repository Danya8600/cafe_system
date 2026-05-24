from datetime import datetime
from decimal import Decimal

from app.extensions import db
from app.models import (
    OrderRecord,
    OrderItemRecord,
    OrderItemExtraRecord,
)
from app.repositories.reference_repository import ReferenceRepository


class OrderRepository:
    @staticmethod
    def save_order(order, customer_id, menu_item, extras):
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
            accepted_at=None
        )

        db.session.add(order_record)
        db.session.flush()

        order_item = OrderItemRecord(
            order_id=order_record.id,
            menu_item_id=menu_item.id,
            quantity=1,
            base_price=Decimal(menu_item.price)
        )

        db.session.add(order_item)
        db.session.flush()

        for extra in extras:
            order_item_extra = OrderItemExtraRecord(
                order_item_id=order_item.id,
                extra_id=extra.id,
                extra_price=Decimal(extra.price)
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