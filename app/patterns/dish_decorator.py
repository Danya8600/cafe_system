from abc import ABC, abstractmethod
from decimal import Decimal


class DishComponent(ABC):
    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_price(self) -> Decimal:
        pass


class BaseDish(DishComponent):
    def __init__(self, menu_item):
        self.menu_item = menu_item

    def get_name(self) -> str:
        return self.menu_item.name

    def get_price(self) -> Decimal:
        return Decimal(self.menu_item.price)


class DishDecorator(DishComponent):
    def __init__(self, dish: DishComponent):
        self.dish = dish

    def get_name(self) -> str:
        return self.dish.get_name()

    def get_price(self) -> Decimal:
        return self.dish.get_price()


class ExtraDecorator(DishDecorator):
    def __init__(self, dish: DishComponent, extra):
        super().__init__(dish)
        self.extra = extra

    def get_name(self) -> str:
        return f"{self.dish.get_name()} + {self.extra.name}"

    def get_price(self) -> Decimal:
        return self.dish.get_price() + Decimal(self.extra.price)


class DishBuilder:
    @staticmethod
    def build(menu_item, extras):
        dish = BaseDish(menu_item)

        for extra in extras:
            dish = ExtraDecorator(dish, extra)

        return dish