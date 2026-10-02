from abc import ABC, abstractmethod
import uuid
from enum import Enum


class Status(Enum):
    ACTIVE = "active"
    CLOSED = "closed"
    FROZEN = "frozen"


class Currency(Enum):
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"
    KZT = "KZT"
    CNY = "CNY"


class AccountFrozenError(Exception):
    pass


class AccountClosedError(Exception):
    pass


class InvalidOperationError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


class AbstractAccount(ABC):

    def __init__(
            self,
            account_id,
            personal_info,
            account_balance,
            account_status
    ):
        self.account_id = account_id
        self.personal_info = personal_info
        self._account_balance = account_balance
        self.account_status = account_status

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def get_account_info(self):
        pass


class BankAccount(AbstractAccount):

    def __init__(
            self,
            personal_info,
            account_balance=0,
            account_id=None,
            account_status=Status.ACTIVE,
            currency=Currency.RUB
    ):
        # Генерация короткого UUID, если ID не передан
        if account_id is None:
            account_id = str(uuid.uuid4())[:8]

        # Валидация ID
        if not isinstance(account_id, str) or not account_id:
            raise InvalidOperationError("Invalid account ID")

        # Валидация данных владельца
        if not isinstance(personal_info, str) or not personal_info.strip():
            raise InvalidOperationError("Invalid personal information")

        # Валидация начального баланса
        if not isinstance(account_balance, (int, float)):
            raise InvalidOperationError("Account balance must be a number")

        if account_balance < 0:
            raise InvalidOperationError("Account balance cannot be negative")

        # Валидация статуса
        if not isinstance(account_status, Status):
            raise InvalidOperationError("Invalid account status")

        # Валидация валюты
        if not isinstance(currency, Currency):
            raise InvalidOperationError("Invalid currency")

        super().__init__(
            account_id,
            personal_info,
            account_balance,
            account_status
        )

        self.currency = currency

    def _check_operation_allowed(self):
        if self.account_status == Status.FROZEN:
            raise AccountFrozenError("Account is frozen")

        if self.account_status == Status.CLOSED:
            raise AccountClosedError("Account is closed")

    def _validate_amount(self, amount):
        if not isinstance(amount, (int, float)):
            raise InvalidOperationError("Amount must be a number")

        if amount <= 0:
            raise InvalidOperationError("Amount must be greater than zero")

    def deposit(self, amount):
        self._check_operation_allowed()
        self._validate_amount(amount)

        self._account_balance += amount

    def withdraw(self, amount):
        self._check_operation_allowed()
        self._validate_amount(amount)

        if self._account_balance < amount:
            raise InsufficientFundsError("Insufficient funds")

        self._account_balance -= amount

    def get_account_info(self):
        return {
            "account_id": self.account_id,
            "personal_info": self.personal_info,
            "balance": self._account_balance,
            "status": self.account_status.value,
            "currency": self.currency.value
        }

    def __str__(self):
        return (
            f"BankAccount | "
            f"Client: {self.personal_info} | "
            f"Account: ****{self.account_id[-4:]} | "
            f"Status: {self.account_status.value} | "
            f"Balance: {self._account_balance} {self.currency.value}"
        )
