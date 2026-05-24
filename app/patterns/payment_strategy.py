from abc import ABC, abstractmethod


class PaymentResult:
    def __init__(self, success: bool, message: str):
        self.success = success
        self.message = message

    def is_success(self) -> bool:
        return self.success

    def get_message(self) -> str:
        return self.message


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self, amount):
        pass

    @abstractmethod
    def get_payment_name(self) -> str:
        pass


class CashPaymentStrategy(PaymentStrategy):
    def pay(self, amount):
        return PaymentResult(
            True,
            f"Оплата наличными выбрана. Сумма к оплате: {amount} руб."
        )

    def get_payment_name(self) -> str:
        return "Наличные"


class BonusPaymentStrategy(PaymentStrategy):
    def pay(self, amount):
        return PaymentResult(
            True,
            f"Оплата бонусами выбрана. Сумма списания: {amount} бонусов."
        )

    def get_payment_name(self) -> str:
        return "Бонусы"


class PaymentContext:
    def __init__(self):
        self.strategy = None

    def set_strategy(self, strategy: PaymentStrategy):
        self.strategy = strategy

    def execute_payment(self, amount):
        if self.strategy is None:
            return PaymentResult(False, "Способ оплаты не выбран.")

        return self.strategy.pay(amount)


class PaymentStrategyFactory:
    @staticmethod
    def create_strategy(payment_method):
        if payment_method.name == "cash":
            return CashPaymentStrategy()

        if payment_method.name == "bonus":
            return BonusPaymentStrategy()

        raise ValueError("Неизвестный способ оплаты.")