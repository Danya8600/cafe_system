from app.models import OrderType, PaymentMethod, OrderStatus


class ReferenceRepository:
    @staticmethod
    def get_order_types():
        return OrderType.query.order_by(OrderType.id).all()

    @staticmethod
    def get_payment_methods():
        return PaymentMethod.query.order_by(PaymentMethod.id).all()

    @staticmethod
    def get_order_statuses():
        return OrderStatus.query.order_by(OrderStatus.id).all()

    @staticmethod
    def get_status_by_name(name):
        return OrderStatus.query.filter_by(name=name).first()

    @staticmethod
    def get_status_by_id(status_id):
        return OrderStatus.query.get(status_id)

    @staticmethod
    def get_order_type_by_name(name):
        return OrderType.query.filter_by(name=name).first()

    @staticmethod
    def get_payment_method_by_name(name):
        return PaymentMethod.query.filter_by(name=name).first()

    @staticmethod
    def get_order_type_by_id(order_type_id):
        return OrderType.query.get(order_type_id)

    @staticmethod
    def get_payment_method_by_id(payment_method_id):
        return PaymentMethod.query.get(payment_method_id)