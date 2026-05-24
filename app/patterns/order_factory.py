from abc import ABC, abstractmethod
from decimal import Decimal


class DomainOrder(ABC):
    def __init__(self, dish, address, payment_method, order_type):
        self.dish = dish
        self.address = address
        self.payment_method = payment_method
        self.order_type = order_type

    @abstractmethod
    def calculate_total(self) -> Decimal:
        pass

    @abstractmethod
    def get_order_info(self) -> str:
        pass


class DeliveryOrder(DomainOrder):
    DELIVERY_PRICE = Decimal("100.00")

    def calculate_total(self) -> Decimal:
        return self.dish.get_price() + self.DELIVERY_PRICE

    def get_order_info(self) -> str:
        return "Заказ с доставкой"


class PickupOrder(DomainOrder):
    def calculate_total(self) -> Decimal:
        return self.dish.get_price()

    def get_order_info(self) -> str:
        return "Заказ самовывозом"


class OrderCreator(ABC):
    @abstractmethod
    def create_order(self, dish, address, payment_method, order_type) -> DomainOrder:
        pass


class DeliveryOrderCreator(OrderCreator):
    def create_order(self, dish, address, payment_method, order_type) -> DeliveryOrder:
        return DeliveryOrder(dish, address, payment_method, order_type)


class PickupOrderCreator(OrderCreator):
    def create_order(self, dish, address, payment_method, order_type) -> PickupOrder:
        return PickupOrder(dish, address, payment_method, order_type)


class OrderFactory:
    @staticmethod
    def create_order(order_type, dish, address, payment_method) -> DomainOrder:
        if order_type.name == "delivery":
            creator = DeliveryOrderCreator()
        elif order_type.name == "pickup":
            creator = PickupOrderCreator()
        else:
            raise ValueError("Неизвестный тип заказа.")

        return creator.create_order(dish, address, payment_method, order_type)