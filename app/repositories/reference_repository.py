from app.models import OrderType, PaymentMethod, OrderStatus


class ReferenceRepository:
    @staticmethod
    def get_order_types():
        return OrderType.query.order_by(OrderType.id).all()

    @staticmethod
    def get_payment_methods():
        return PaymentMethod.query.order_by(PaymentMethod.id).all()

    @staticmethod
    def get_status_by_name(name):
        return OrderStatus.query.filter_by(name=name).first()

    @staticmethod
    def get_order_type_by_name(name):
        return OrderType.query.filter_by(name=name).first()

    @staticmethod
    def get_payment_method_by_name(name):
        return PaymentMethod.query.filter_by(name=name).first()