from abc import ABC, abstractmethod
from decimal import Decimal


class OrderLine:
    def __init__(self, menu_item, dish, extras, quantity):
        self.menu_item = menu_item
        self.dish = dish
        self.extras = extras
        self.quantity = quantity

    def calculate_total(self) -> Decimal:
        return self.dish.get_price() * self.quantity


class DomainOrder(ABC):
    def __init__(self, order_lines, address, payment_method, order_type):
        self.order_lines = order_lines
        self.address = address
        self.payment_method = payment_method
        self.order_type = order_type

    def calculate_items_total(self) -> Decimal:
        total = Decimal("0.00")

        for line in self.order_lines:
            total += line.calculate_total()

        return total

    @abstractmethod
    def calculate_total(self) -> Decimal:
        pass

    @abstractmethod
    def get_order_info(self) -> str:
        pass


class DeliveryOrder(DomainOrder):
    DELIVERY_PRICE = Decimal("100.00")

    def calculate_total(self) -> Decimal:
        return self.calculate_items_total() + self.DELIVERY_PRICE

    def get_order_info(self) -> str:
        return "Заказ с доставкой"


class PickupOrder(DomainOrder):
    def calculate_total(self) -> Decimal:
        return self.calculate_items_total()

    def get_order_info(self) -> str:
        return "Заказ самовывозом"


class OrderCreator(ABC):
    @abstractmethod
    def create_order(self, order_lines, address, payment_method, order_type) -> DomainOrder:
        pass


class DeliveryOrderCreator(OrderCreator):
    def create_order(self, order_lines, address, payment_method, order_type) -> DeliveryOrder:
        return DeliveryOrder(order_lines, address, payment_method, order_type)


class PickupOrderCreator(OrderCreator):
    def create_order(self, order_lines, address, payment_method, order_type) -> PickupOrder:
        return PickupOrder(order_lines, address, payment_method, order_type)


class OrderFactory:
    @staticmethod
    def create_order(order_type, order_lines, address, payment_method) -> DomainOrder:
        if order_type.name == "delivery":
            creator = DeliveryOrderCreator()
        elif order_type.name == "pickup":
            creator = PickupOrderCreator()
        else:
            raise ValueError("Неизвестный тип заказа.")

        return creator.create_order(order_lines, address, payment_method, order_type)