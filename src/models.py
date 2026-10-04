import csv
import heapq
import json
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from decimal import Decimal
from enum import Enum

import matplotlib.pyplot as plt
from pathlib import Path


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


class AccountType(Enum):
    BASE = "Base"
    SAVINGS = "Savings"
    PREMIUM = "Premium"
    INVESTMENT = "Investment"


class AssetType(Enum):
    STOCKS = "Stocks"
    BONDS = "Bonds"
    ETF = "ETF"


class TransactionType(Enum):
    TRANSFER = "transfer"
    DEPOSIT = "deposit"
    WITHDRAW = "withdraw"


class TransactionStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AuditLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class RiskLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AccountFrozenError(Exception):
    pass


class AccountClosedError(Exception):
    pass


class InvalidOperationError(Exception):
    pass


class InsufficientFundsError(Exception):
    pass


def _to_money(value) -> Decimal:
    return Decimal(str(value))


class AbstractAccount(ABC):

    def __init__(
            self,
            account_id,
            personal_info,
            account_balance,
            account_status,
            account_type
    ):
        self.account_id = account_id
        self.personal_info = personal_info
        self._account_balance = _to_money(account_balance)
        self.account_status = account_status
        self.account_type = account_type

    @abstractmethod
    def deposit(self, amount):
        pass

    @abstractmethod
    def withdraw(self, amount):
        pass

    @abstractmethod
    def get_account_info(self):
        pass

    @property
    def balance(self):
        return self._account_balance

    def _check_operation_allowed(self):
        if self.account_status == Status.FROZEN:
            raise AccountFrozenError("Account is frozen")

        if self.account_status == Status.CLOSED:
            raise AccountClosedError("Account is closed")

    def _validate_amount(self, amount):
        if not isinstance(amount, (int, float, Decimal)):
            raise InvalidOperationError("Amount must be a number")

        if amount <= 0:
            raise InvalidOperationError(
                "Amount must be greater than zero"
            )

        return _to_money(amount)


class BankAccount(AbstractAccount):

    def __init__(
            self,
            personal_info,
            account_type=AccountType.BASE,
            account_balance=0,
            account_id=None,
            account_status=Status.ACTIVE,
            currency=Currency.RUB
    ):
        if account_id is None:
            account_id = str(uuid.uuid4())[:8]

        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidOperationError("Invalid account ID")

        if not isinstance(personal_info, str) or not personal_info.strip():
            raise InvalidOperationError(
                "Invalid personal information"
            )

        if not isinstance(account_balance, (int, float, Decimal)):
            raise InvalidOperationError(
                "Account balance must be a number"
            )

        if account_balance < 0:
            raise InvalidOperationError(
                "Account balance cannot be negative"
            )

        if not isinstance(account_status, Status):
            raise InvalidOperationError(
                "Invalid account status"
            )

        if not isinstance(currency, Currency):
            raise InvalidOperationError(
                "Invalid currency"
            )

        if not isinstance(account_type, AccountType):
            raise InvalidOperationError(
                "Invalid account type"
            )

        super().__init__(
            account_id,
            personal_info,
            account_balance,
            account_status,
            account_type
        )

        self.currency = currency

    def deposit(self, amount):
        self._check_operation_allowed()
        amount = self._validate_amount(amount)

        self._account_balance += amount

    def withdraw(self, amount):
        self._check_operation_allowed()
        amount = self._validate_amount(amount)

        if self._account_balance < amount:
            raise InsufficientFundsError(
                "Insufficient funds"
            )

        self._account_balance -= amount

    def get_account_info(self):
        return {
            "account_id": self.account_id,
            "personal_info": self.personal_info,
            "balance": self._account_balance,
            "status": self.account_status.value,
            "currency": self.currency.value,
            "account_type": self.account_type.value
        }

    def __str__(self):
        return (
            f"BankAccount | "
            f"Client: {self.personal_info} | "
            f"Account: ****{self.account_id[-4:]} | "
            f"Status: {self.account_status.value} | "
            f"Balance: {self._account_balance} "
            f"{self.currency.value} | "
            f"Account Type: {self.account_type.value}"
        )


class SavingsAccount(AbstractAccount):

    def __init__(
            self,
            personal_info,
            min_balance,
            monthly_interest_rate,
            account_type=AccountType.SAVINGS,
            account_balance=0,
            account_id=None,
            account_status=Status.ACTIVE,
            currency=Currency.RUB
    ):
        if account_id is None:
            account_id = str(uuid.uuid4())[:8]

        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidOperationError("Invalid account ID")

        if not isinstance(personal_info, str) or not personal_info.strip():
            raise InvalidOperationError(
                "Invalid personal information"
            )

        if not isinstance(account_balance, (int, float, Decimal)):
            raise InvalidOperationError(
                "Account balance must be a number"
            )

        if account_balance < 0:
            raise InvalidOperationError(
                "Account balance cannot be negative"
            )

        if not isinstance(min_balance, (int, float, Decimal)):
            raise InvalidOperationError(
                "Minimum balance must be a number"
            )

        if min_balance < 0:
            raise InvalidOperationError(
                "Minimum balance cannot be negative"
            )

        if not isinstance(monthly_interest_rate, (int, float, Decimal)):
            raise InvalidOperationError(
                "Interest rate must be a number"
            )

        if monthly_interest_rate < 0:
            raise InvalidOperationError(
                "Interest rate cannot be negative"
            )

        if not isinstance(account_status, Status):
            raise InvalidOperationError(
                "Invalid account status"
            )

        if not isinstance(currency, Currency):
            raise InvalidOperationError(
                "Invalid currency"
            )

        if not isinstance(account_type, AccountType):
            raise InvalidOperationError(
                "Invalid account type"
            )

        super().__init__(
            account_id,
            personal_info,
            account_balance,
            account_status,
            account_type
        )

        self.currency = currency
        self.min_balance = _to_money(min_balance)
        self.monthly_interest_rate = _to_money(monthly_interest_rate)

    def deposit(self, amount):
        self._check_operation_allowed()
        amount = self._validate_amount(amount)

        self._account_balance += amount

    def withdraw(self, amount):
        self._check_operation_allowed()
        amount = self._validate_amount(amount)

        if self._account_balance < amount:
            raise InsufficientFundsError(
                "Insufficient funds"
            )

        if self._account_balance - amount < self.min_balance:
            raise InsufficientFundsError(
                "Minimal balance level has been reached"
            )

        self._account_balance -= amount

    def apply_monthly_interest(self):
        self._check_operation_allowed()

        interest = (
                self._account_balance
                * self.monthly_interest_rate
        ).quantize(Decimal("0.01"))

        self._account_balance += interest

    def get_account_info(self):
        return {
            "account_id": self.account_id,
            "personal_info": self.personal_info,
            "balance": self._account_balance,
            "status": self.account_status.value,
            "currency": self.currency.value,
            "account_type": self.account_type.value
        }

    def __str__(self):
        return (
            f"SavingsAccount | "
            f"Client: {self.personal_info} | "
            f"Account: ****{self.account_id[-4:]} | "
            f"Status: {self.account_status.value} | "
            f"Balance: {self._account_balance} "
            f"{self.currency.value} | "
            f"Account Type: {self.account_type.value}"
        )


class PremiumAccount(AbstractAccount):

    def __init__(
            self,
            personal_info,
            overdraft_limit=Decimal("0.00"),
            commission=Decimal("2.00"),
            account_type=AccountType.PREMIUM,
            account_balance=0,
            account_id=None,
            account_status=Status.ACTIVE,
            currency=Currency.RUB
    ):
        if account_id is None:
            account_id = str(uuid.uuid4())[:8]

        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidOperationError("Invalid account ID")

        if not isinstance(personal_info, str) or not personal_info.strip():
            raise InvalidOperationError(
                "Invalid personal information"
            )

        if not isinstance(account_balance, (int, float, Decimal)):
            raise InvalidOperationError(
                "Account balance must be a number"
            )

        if account_balance < 0:
            raise InvalidOperationError(
                "Account balance cannot be negative"
            )

        if not isinstance(overdraft_limit, (int, float, Decimal)):
            raise InvalidOperationError(
                "Overdraft limit must be a number"
            )

        if overdraft_limit < 0:
            raise InvalidOperationError(
                "Overdraft limit cannot be negative"
            )

        if not isinstance(commission, Decimal):
            raise InvalidOperationError(
                "Commission must be Decimal"
            )

        if commission < 0:
            raise InvalidOperationError(
                "Commission cannot be negative"
            )

        if not isinstance(account_status, Status):
            raise InvalidOperationError(
                "Invalid account status"
            )

        if not isinstance(currency, Currency):
            raise InvalidOperationError(
                "Invalid currency"
            )

        if not isinstance(account_type, AccountType):
            raise InvalidOperationError(
                "Invalid account type"
            )

        super().__init__(
            account_id,
            personal_info,
            account_balance,
            account_status,
            account_type
        )

        self.currency = currency
        self.overdraft_limit = _to_money(overdraft_limit)
        self.commission = commission

    def deposit(self, amount):
        self._check_operation_allowed()
        amount = self._validate_amount(amount)

        self._account_balance += amount

    def withdraw(self, amount):
        self._check_operation_allowed()
        amount = self._validate_amount(amount)

        total_amount = amount + self.commission

        if self._account_balance - total_amount < -self.overdraft_limit:
            raise InsufficientFundsError(
                "Insufficient funds"
            )

        self._account_balance -= total_amount

    def get_account_info(self):
        return {
            "account_id": self.account_id,
            "personal_info": self.personal_info,
            "balance": self._account_balance,
            "status": self.account_status.value,
            "currency": self.currency.value,
            "account_type": self.account_type.value,
            "overdraft_limit": self.overdraft_limit,
            "commission": self.commission
        }

    def __str__(self):
        return (
            f"PremiumAccount | "
            f"Client: {self.personal_info} | "
            f"Account: ****{self.account_id[-4:]} | "
            f"Status: {self.account_status.value} | "
            f"Balance: {self._account_balance} "
            f"{self.currency.value} | "
            f"Account Type: {self.account_type.value}"
        )


class InvestmentAccount(AbstractAccount):

    def __init__(
            self,
            personal_info,
            account_balance=0,
            account_id=None,
            account_status=Status.ACTIVE,
            currency=Currency.RUB,
            account_type=AccountType.INVESTMENT
    ):
        if account_id is None:
            account_id = str(uuid.uuid4())[:8]

        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidOperationError("Invalid account ID")

        if not isinstance(personal_info, str) or not personal_info.strip():
            raise InvalidOperationError(
                "Invalid personal information"
            )

        if not isinstance(account_balance, (int, float, Decimal)):
            raise InvalidOperationError(
                "Account balance must be a number"
            )

        if account_balance < 0:
            raise InvalidOperationError(
                "Account balance cannot be negative"
            )

        if not isinstance(account_status, Status):
            raise InvalidOperationError(
                "Invalid account status"
            )

        if not isinstance(currency, Currency):
            raise InvalidOperationError(
                "Invalid currency"
            )

        if account_type != AccountType.INVESTMENT:
            raise InvalidOperationError(
                "Investment account must have Investment account type"
            )

        super().__init__(
            account_id,
            personal_info,
            account_balance,
            account_status,
            account_type
        )

        self.currency = currency

        self.portfolio: dict[AssetType, Decimal] = {
            asset: Decimal("0.00")
            for asset in AssetType
        }

    @property
    def portfolio_value(self) -> Decimal:
        return sum(
            self.portfolio.values(),
            Decimal("0.00")
        )

    @property
    def total_balance(self) -> Decimal:
        return (
                Decimal(str(self._account_balance))
                + self.portfolio_value
        )

    @property
    def portfolio_distribution(self) -> dict[AssetType, Decimal]:
        total = self.portfolio_value

        if total == 0:
            return {
                asset: Decimal("0.00")
                for asset in AssetType
            }

        return {
            asset: (
                    amount / total * Decimal("100")
            ).quantize(Decimal("0.01"))
            for asset, amount in self.portfolio.items()
        }

    def deposit(
            self,
            asset: AssetType,
            amount: Decimal
    ):
        self._check_operation_allowed()

        if not isinstance(asset, AssetType):
            raise InvalidOperationError(
                "Invalid asset type"
            )

        if not isinstance(amount, Decimal):
            raise InvalidOperationError(
                "Amount must be Decimal"
            )

        if amount <= 0:
            raise InvalidOperationError(
                "Amount must be positive"
            )

        if Decimal(str(self._account_balance)) < amount:
            raise InsufficientFundsError(
                "Insufficient funds"
            )

        self._account_balance -= amount
        self.portfolio[asset] += amount

    def withdraw(
            self,
            asset: AssetType,
            amount: Decimal
    ):
        self._check_operation_allowed()

        if not isinstance(asset, AssetType):
            raise InvalidOperationError(
                "Invalid asset type"
            )

        if not isinstance(amount, Decimal):
            raise InvalidOperationError(
                "Amount must be Decimal"
            )

        if amount <= 0:
            raise InvalidOperationError(
                "Amount must be positive"
            )

        if amount > self.portfolio[asset]:
            raise InsufficientFundsError(
                "Insufficient funds in asset"
            )

        self.portfolio[asset] -= amount
        self._account_balance += Decimal(amount)

    def project_yearly_growth(
            self,
            growth_rates: dict[AssetType, Decimal]
    ) -> Decimal:

        if not isinstance(growth_rates, dict):
            raise InvalidOperationError(
                "Growth rates must be a dictionary"
            )

        total_growth = Decimal("0.00")

        for asset, growth_rate in growth_rates.items():

            if not isinstance(asset, AssetType):
                raise InvalidOperationError(
                    "Invalid asset type"
                )

            if not isinstance(growth_rate, Decimal):
                raise InvalidOperationError(
                    "Growth rate must be Decimal"
                )

            if growth_rate <= 0:
                raise InvalidOperationError(
                    "Growth rate must be positive"
                )

            asset_amount = self.portfolio[asset]

            total_growth += (
                    asset_amount * growth_rate
            )

        return total_growth.quantize(
            Decimal("0.01")
        )

    def get_account_info(self):
        return {
            "account_id": self.account_id,
            "personal_info": self.personal_info,
            "balance": self._account_balance,
            "portfolio_value": self.portfolio_value,
            "total_balance": self.total_balance,
            "status": self.account_status.value,
            "currency": self.currency.value,
            "account_type": self.account_type.value,
            "portfolio": {
                asset.value: amount
                for asset, amount in self.portfolio.items()
            },
            "portfolio_distribution": {
                asset.value: percentage
                for asset, percentage
                in self.portfolio_distribution.items()
            }
        }

    def __str__(self):
        portfolio = ", ".join(
            f"{asset.value}: {amount}"
            for asset, amount in self.portfolio.items()
            if amount > 0
        )

        return (
            f"InvestmentAccount | "
            f"Client: {self.personal_info} | "
            f"Account: ****{self.account_id[-4:]} | "
            f"Status: {self.account_status.value} | "
            f"Balance: {self._account_balance} "
            f"{self.currency.value} | "
            f"Account Type: {self.account_type.value} | "
            f"Portfolio: [{portfolio}]"
        )


class Client:

    def __init__(
            self,
            client_id: str,
            personal_info: str,
            status: Status,
            accounts: set[str],
            contacts: dict[str, str],
            age: int,
            password: str
    ):
        if not isinstance(client_id, str) or not client_id.strip():
            raise InvalidOperationError("Invalid client ID")

        if not isinstance(personal_info, str) or not personal_info.strip():
            raise InvalidOperationError(
                "Invalid personal information"
            )

        if not isinstance(status, Status):
            raise InvalidOperationError(
                "Invalid client status"
            )

        if not isinstance(accounts, set):
            raise InvalidOperationError(
                "Accounts must be a set"
            )

        if not all(
                isinstance(account_id, str)
                and account_id.strip()
                for account_id in accounts
        ):
            raise InvalidOperationError(
                "Invalid account ID in accounts"
            )

        if not isinstance(contacts, dict):
            raise InvalidOperationError(
                "Contacts must be a dictionary"
            )

        if not all(
                isinstance(key, str)
                and key.strip()
                and isinstance(value, str)
                and value.strip()
                for key, value in contacts.items()
        ):
            raise InvalidOperationError(
                "Invalid contacts"
            )

        if not isinstance(age, int) or isinstance(age, bool):
            raise InvalidOperationError(
                "Age must be an integer"
            )

        if age < 18:
            raise InvalidOperationError(
                "Client must be at least 18 years old"
            )

        if not isinstance(password, str) or not password:
            raise InvalidOperationError(
                "Invalid password"
            )

        self.client_id = client_id
        self.personal_info = personal_info
        self.status = status
        self.accounts = accounts
        self.contacts = contacts
        self.age = age
        self.password = password

        self.failed_attempts = 0
        self.is_blocked = False

    def add_account(self, account_id: str):
        if not isinstance(account_id, str) or not account_id.strip():
            raise InvalidOperationError(
                "Invalid account ID"
            )

        self.accounts.add(account_id)

    def remove_account(self, account_id: str):
        if account_id not in self.accounts:
            raise InvalidOperationError(
                "Account not found"
            )

        self.accounts.remove(account_id)

    def __str__(self):
        return (
            f"Client | "
            f"ID: {self.client_id} | "
            f"Name: {self.personal_info} | "
            f"Status: {self.status.value} | "
            f"Age: {self.age} | "
            f"Accounts: {len(self.accounts)}"
        )


def assess_risk(
        risk_analyzer,
        transaction,
        history,
        involved_ids: set,
        new_account: bool
):
    related = [
        past
        for past in history
        if past.sender in involved_ids or past.receiver in involved_ids
    ]

    return risk_analyzer.analyze(
        transaction,
        related,
        new_account=new_account
    )


class Bank:

    def __init__(
            self,
            risk_analyzer: "RiskAnalyzer | None" = None,
            audit_log: "AuditLog | None" = None
    ):
        self.clients: dict[str, Client] = {}
        self.accounts: dict[str, AbstractAccount] = {}
        self.suspicious_actions: list[dict] = []
        self.risk_analyzer = (
            risk_analyzer if risk_analyzer is not None
            else RiskAnalyzer()
        )
        self.audit_log = audit_log
        self.history = []

    def add_client(self, client: Client):
        if not isinstance(client, Client):
            raise InvalidOperationError(
                "Invalid client"
            )

        if client.client_id in self.clients:
            raise InvalidOperationError(
                "Client already exists"
            )

        self.clients[client.client_id] = client

    def open_account(
            self,
            client_id: str,
            account: AbstractAccount
    ):
        self._check_operation_time()

        client = self._get_client(client_id)

        if not isinstance(account, AbstractAccount):
            raise InvalidOperationError(
                "Invalid account"
            )

        if account.account_id in self.accounts:
            raise InvalidOperationError(
                "Account already exists"
            )

        self.accounts[account.account_id] = account
        client.add_account(account.account_id)

    def close_account(
            self,
            client_id: str,
            account_id: str,
            password: str
    ):
        self._check_operation_time()

        account = self._authenticate_and_get_account(
            client_id,
            account_id,
            password
        )

        account.account_status = Status.CLOSED

    def freeze_account(
            self,
            client_id: str,
            account_id: str,
            password: str
    ):
        self._check_operation_time()

        account = self._authenticate_and_get_account(
            client_id,
            account_id,
            password
        )

        account.account_status = Status.FROZEN

    def unfreeze_account(
            self,
            client_id: str,
            account_id: str,
            password: str
    ):
        self._check_operation_time()

        account = self._authenticate_and_get_account(
            client_id,
            account_id,
            password
        )

        account.account_status = Status.ACTIVE

    def search_accounts(self, client_id: str):
        client = self._get_client(client_id)

        return [
            self.accounts[account_id]
            for account_id in client.accounts
            if account_id in self.accounts
        ]

    def authenticate_client(
            self,
            client_id: str,
            password: str
    ):
        client = self._get_client(client_id)

        if client.is_blocked:
            raise InvalidOperationError(
                "Client is blocked"
            )

        if client.password != password:
            client.failed_attempts += 1

            self.suspicious_actions.append({
                "client_id": client_id,
                "action": "failed_authentication",
                "attempt": client.failed_attempts,
                "timestamp": datetime.now().isoformat()
            })

            if client.failed_attempts >= 3:
                client.is_blocked = True

            raise InvalidOperationError(
                "Invalid password"
            )

        client.failed_attempts = 0

        return True

    def deposit(
            self,
            client_id: str,
            account_id: str,
            password: str,
            amount
    ):
        self._check_operation_time()

        account = self._authenticate_and_get_account(
            client_id,
            account_id,
            password
        )

        self._guarded_operation(
            client_id,
            account,
            TransactionType.DEPOSIT,
            amount,
            account.deposit
        )

    def withdraw(
            self,
            client_id: str,
            account_id: str,
            password: str,
            amount
    ):
        self._check_operation_time()

        account = self._authenticate_and_get_account(
            client_id,
            account_id,
            password
        )

        self._guarded_operation(
            client_id,
            account,
            TransactionType.WITHDRAW,
            amount,
            account.withdraw
        )

    def _guarded_operation(
            self,
            client_id: str,
            account,
            transaction_type: TransactionType,
            amount,
            operation
    ):
        if not isinstance(amount, (int, float, Decimal)):
            raise InvalidOperationError(
                "Amount must be a number"
            )

        is_deposit = transaction_type == TransactionType.DEPOSIT

        transaction = Transaction(
            transaction_type=transaction_type,
            amount=_to_money(amount),
            currency=account.currency,
            sender=None if is_deposit else account.account_id,
            receiver=account.account_id if is_deposit else None,
        )

        client = self._get_client(client_id)

        account_is_new = not any(
            past.status == TransactionStatus.COMPLETED
            and account.account_id in (past.sender, past.receiver)
            for past in self.history
        )

        risk = assess_risk(
            self.risk_analyzer,
            transaction,
            self.history,
            set(client.accounts) | {account.account_id},
            account_is_new
        )

        transaction.risk_level = risk["risk_level"]
        self.history.append(transaction)

        if self.risk_analyzer.is_dangerous(risk):
            transaction.mark_failed("Blocked: high risk")

            self._record(
                client_id,
                transaction,
                AuditLevel.CRITICAL,
                "OPERATION_BLOCKED",
                ", ".join(risk["reasons"])
            )

            raise InvalidOperationError(
                "Operation blocked: high risk"
            )

        try:
            operation(amount)

        except Exception as error:
            transaction.mark_failed(str(error))

            self._record(
                client_id,
                transaction,
                AuditLevel.ERROR,
                "OPERATION_FAILED",
                str(error)
            )

            raise

        transaction.mark_completed()

        if is_deposit:
            transaction.credited_amount = transaction.amount
        else:
            transaction.debited_amount = transaction.amount

        self._record(
            client_id,
            transaction,
            AuditLevel.INFO,
            "OPERATION_COMPLETED",
            transaction_type.value
        )

    def _record(
            self,
            client_id: str,
            transaction: Transaction,
            level: AuditLevel,
            action: str,
            message: str
    ):
        if self.audit_log is None:
            return

        self.audit_log.log(
            level=level,
            action=action,
            message=message,
            client_id=client_id,
            transaction_id=transaction.transaction_id
        )

    def get_total_balance(self):
        total = Decimal("0.00")

        for account in self.accounts.values():

            if isinstance(account, InvestmentAccount):
                total += account.total_balance

            else:
                total += Decimal(
                    str(account.balance)
                )

        return total

    def get_clients_ranking(self):
        def client_balance(client):
            total = Decimal("0.00")

            for account_id in client.accounts:
                account = self.accounts.get(account_id)

                if account is None:
                    continue

                if isinstance(account, InvestmentAccount):
                    total += account.total_balance
                else:
                    total += Decimal(
                        str(account.balance)
                    )

            return total

        return sorted(
            self.clients.values(),
            key=client_balance,
            reverse=True
        )

    def _get_client(self, client_id: str):
        client = self.clients.get(client_id)

        if client is None:
            raise InvalidOperationError(
                "Client not found"
            )

        return client

    def _authenticate_and_get_account(
            self,
            client_id: str,
            account_id: str,
            password: str
    ):
        self.authenticate_client(
            client_id,
            password
        )

        client = self._get_client(client_id)

        if account_id not in client.accounts:
            raise InvalidOperationError(
                "Client does not own this account"
            )

        account = self.accounts.get(account_id)

        if account is None:
            raise InvalidOperationError(
                "Account not found"
            )

        return account

    def _check_operation_time(self):
        current_hour = datetime.now().hour

        if 0 <= current_hour < 5:
            raise InvalidOperationError(
                "Operations are unavailable "
                "from 00:00 to 05:00"
            )


class Transaction:

    def __init__(
            self,
            transaction_type: TransactionType,
            amount: Decimal,
            currency: Currency,
            sender: str | None = None,
            receiver: str | None = None,
            commission: Decimal = Decimal("0.00"),
            is_external: bool = False
    ):
        if not isinstance(transaction_type, TransactionType):
            raise InvalidOperationError(
                "Invalid transaction type"
            )

        if not isinstance(amount, Decimal) or amount <= 0:
            raise InvalidOperationError(
                "Amount must be positive Decimal"
            )

        if not isinstance(currency, Currency):
            raise InvalidOperationError(
                "Invalid currency"
            )

        if not isinstance(commission, Decimal) or commission < 0:
            raise InvalidOperationError(
                "Invalid commission"
            )

        self.transaction_id = str(uuid.uuid4())[:8]
        self.transaction_type = transaction_type
        self.amount = amount
        self.currency = currency
        self.commission = commission

        self.sender = sender
        self.receiver = receiver

        self.status = TransactionStatus.PENDING
        self.failure_reason = None

        self.created_at = datetime.now()
        self.processed_at = None

        self.is_external = is_external
        self.debited_amount = None
        self.credited_amount = None
        self.risk_level = None

    def mark_processing(self):
        self.status = TransactionStatus.PROCESSING

    def mark_completed(self):
        self.status = TransactionStatus.COMPLETED
        self.processed_at = datetime.now()

    def mark_failed(self, reason: str):
        self.status = TransactionStatus.FAILED
        self.failure_reason = reason
        self.processed_at = datetime.now()

    def cancel(self):
        if self.status != TransactionStatus.PENDING:
            raise InvalidOperationError(
                "Only pending transaction can be cancelled"
            )

        self.status = TransactionStatus.CANCELLED
        self.processed_at = datetime.now()

    def __str__(self):
        return (
            f"Transaction | "
            f"ID: {self.transaction_id} | "
            f"Type: {self.transaction_type.value} | "
            f"Amount: {self.amount} "
            f"{self.currency.value} | "
            f"Status: {self.status.value}"
        )


class TransactionQueue:

    def __init__(self):
        self._ready = []
        self._delayed = []
        self._counter = 0

    def add(
            self,
            transaction: Transaction,
            priority: int = 0,
            execute_at: datetime | None = None
    ):
        if not isinstance(transaction, Transaction):
            raise InvalidOperationError(
                "Invalid transaction"
            )

        if not isinstance(priority, int) or isinstance(priority, bool):
            raise InvalidOperationError(
                "Priority must be an integer"
            )

        self._counter += 1

        if execute_at is None or execute_at <= datetime.now():
            heapq.heappush(
                self._ready,
                (-priority, self._counter, transaction)
            )
        else:
            heapq.heappush(
                self._delayed,
                (execute_at, self._counter, priority, transaction)
            )

    def pop(self):
        self._release_due()

        if not self._ready:
            return None

        _, _, transaction = heapq.heappop(self._ready)

        return transaction

    def cancel(self, transaction_id: str):
        for heap in (self._ready, self._delayed):
            for index, item in enumerate(heap):

                transaction = item[-1]

                if transaction.transaction_id == transaction_id:
                    transaction.cancel()

                    heap.pop(index)
                    heapq.heapify(heap)

                    return

        raise InvalidOperationError(
            "Transaction not found"
        )

    def _release_due(self):
        now = datetime.now()

        while self._delayed and self._delayed[0][0] <= now:
            _, counter, priority, transaction = heapq.heappop(
                self._delayed
            )

            heapq.heappush(
                self._ready,
                (-priority, counter, transaction)
            )

    def __len__(self):
        return len(self._ready) + len(self._delayed)

    def is_empty(self):
        return len(self) == 0


class TransactionProcessor:

    def __init__(
            self,
            bank: Bank,
            external_transfer_commission: Decimal = Decimal("0.01"),
            max_retries: int = 3,
            exchange_rates: dict | None = None,
            risk_analyzer: "RiskAnalyzer | None" = None,
            audit_log: "AuditLog | None" = None
    ):
        if not isinstance(
                external_transfer_commission,
                Decimal
        ):
            raise InvalidOperationError(
                "Commission must be Decimal"
            )

        if external_transfer_commission < 0:
            raise InvalidOperationError(
                "Commission cannot be negative"
            )

        if max_retries <= 0:
            raise InvalidOperationError(
                "Max retries must be positive"
            )

        self.bank = bank
        self.external_transfer_commission = (
            external_transfer_commission
        )
        self.max_retries = max_retries
        self.exchange_rates = (
            exchange_rates if exchange_rates is not None else {}
        )
        self.risk_analyzer = (
            risk_analyzer if risk_analyzer is not None
            else RiskAnalyzer()
        )
        self.audit_log = audit_log

        self.errors = []
        self.history = []

    def calculate_commission(
            self,
            transaction: Transaction
    ) -> Decimal:

        if (
                transaction.transaction_type != TransactionType.TRANSFER
                or not transaction.is_external
        ):
            return Decimal("0.00")

        return (
                transaction.amount
                * self.external_transfer_commission
        ).quantize(Decimal("0.01"))

    def convert_currency(
            self,
            amount: Decimal,
            from_currency: Currency,
            to_currency: Currency,
            exchange_rates: dict
    ) -> Decimal:

        if not isinstance(amount, Decimal):
            raise InvalidOperationError(
                "Amount must be Decimal"
            )

        if from_currency == to_currency:
            return amount

        rate = exchange_rates.get(
            (from_currency, to_currency)
        )

        if rate is None:
            raise InvalidOperationError(
                "Exchange rate not found"
            )

        return (
                amount * rate
        ).quantize(Decimal("0.01"))

    def process(
            self,
            transaction: Transaction
    ):
        if transaction.status != TransactionStatus.PENDING:
            raise InvalidOperationError(
                "Transaction is not pending"
            )

        transaction.mark_processing()

        risk = self._assess_risk(transaction)
        transaction.risk_level = risk["risk_level"]

        if self.risk_analyzer.is_dangerous(risk):
            transaction.mark_failed(
                "Blocked: high risk"
            )

            self._audit(
                AuditLevel.CRITICAL,
                "TRANSACTION_BLOCKED",
                ", ".join(risk["reasons"]),
                transaction
            )

        else:
            self._run_with_retries(transaction)

        self.history.append(transaction)

        return transaction

    def process_queue(
            self,
            queue: TransactionQueue
    ):
        processed = []

        while not queue.is_empty():

            transaction = queue.pop()

            if transaction is None:
                break

            processed.append(
                self.process(transaction)
            )

        return processed

    def _run_with_retries(
            self,
            transaction: Transaction
    ):
        for attempt in range(1, self.max_retries + 1):

            try:
                self._execute(transaction)

            except Exception as error:

                self.errors.append({
                    "transaction_id":
                        transaction.transaction_id,
                    "attempt": attempt,
                    "error": str(error)
                })

                if attempt == self.max_retries:
                    transaction.mark_failed(
                        str(error)
                    )

                    self._audit(
                        AuditLevel.ERROR,
                        "TRANSACTION_FAILED",
                        str(error),
                        transaction
                    )

            else:
                transaction.mark_completed()

                self._audit(
                    AuditLevel.INFO,
                    "TRANSACTION_COMPLETED",
                    transaction.transaction_type.value,
                    transaction
                )

                return

    def _execute(
            self,
            transaction: Transaction
    ):
        sender, receiver = self._resolve_accounts(transaction)
        commission = self.calculate_commission(transaction)

        debit = None
        credit = None

        if sender is not None:
            debit = self.convert_currency(
                transaction.amount + commission,
                transaction.currency,
                sender.currency,
                self.exchange_rates
            )

        if receiver is not None:
            credit = self.convert_currency(
                transaction.amount,
                transaction.currency,
                receiver.currency,
                self.exchange_rates
            )

            receiver._check_operation_allowed()

            if credit <= 0:
                raise InvalidOperationError(
                    "Converted amount is too small"
                )

        if sender is not None:
            sender.withdraw(debit)

        if receiver is not None:
            receiver.deposit(credit)

        transaction.commission = commission
        transaction.debited_amount = debit
        transaction.credited_amount = credit

    def _resolve_accounts(
            self,
            transaction: Transaction
    ):
        if transaction.transaction_type == TransactionType.DEPOSIT:

            if transaction.sender is not None:
                raise InvalidOperationError(
                    "Deposit must not have a sender"
                )

            return None, self._find_account(
                transaction.receiver,
                "Receiver"
            )

        if transaction.transaction_type == TransactionType.WITHDRAW:

            if transaction.receiver is not None:
                raise InvalidOperationError(
                    "Withdraw must not have a receiver"
                )

            return self._find_account(
                transaction.sender,
                "Sender"
            ), None

        return (
            self._find_account(transaction.sender, "Sender"),
            self._find_account(transaction.receiver, "Receiver"),
        )

    def _find_account(
            self,
            account_id: str | None,
            role: str
    ):
        account = self.bank.accounts.get(account_id)

        if account is None:
            raise InvalidOperationError(
                f"{role} account not found"
            )

        if isinstance(account, InvestmentAccount):
            raise InvalidOperationError(
                "Investment accounts do not support transactions"
            )

        return account

    def _assess_risk(
            self,
            transaction: Transaction
    ):
        involved = {
            account_id
            for account_id in (
                transaction.sender,
                transaction.receiver
            )
            if account_id is not None
        }

        receiver_is_new = (
                transaction.transaction_type == TransactionType.TRANSFER
                and not any(
                    past.status == TransactionStatus.COMPLETED
                    and past.receiver == transaction.receiver
                    for past in self.history
                )
        )

        return assess_risk(
            self.risk_analyzer,
            transaction,
            self.history,
            involved,
            receiver_is_new
        )

    def _client_id_for(
            self,
            account_id: str | None
    ):
        if account_id is None:
            return None

        for client in self.bank.clients.values():
            if account_id in client.accounts:
                return client.client_id

        return None

    def _audit(
            self,
            level: AuditLevel,
            action: str,
            message: str,
            transaction: Transaction
    ):
        if self.audit_log is None:
            return

        client_id = (
                self._client_id_for(transaction.sender)
                or self._client_id_for(transaction.receiver)
        )

        self.audit_log.log(
            level=level,
            action=action,
            message=message,
            client_id=client_id,
            transaction_id=transaction.transaction_id
        )


class AuditLog:

    def __init__(
            self,
            file_path: str = "audit.log"
    ):
        self.file_path = file_path
        self.logs = []

    def log(
            self,
            level: AuditLevel,
            action: str,
            message: str,
            client_id: str | None = None,
            transaction_id: str | None = None
    ):
        if not isinstance(level, AuditLevel):
            raise InvalidOperationError(
                "Invalid audit level"
            )

        record = {
            "timestamp": datetime.now().isoformat(),
            "level": level.value,
            "action": action,
            "message": message,
            "client_id": client_id,
            "transaction_id": transaction_id
        }

        self.logs.append(record)

        with open(
                self.file_path,
                "a",
                encoding="utf-8"
        ) as file:
            file.write(
                json.dumps(
                    record,
                    ensure_ascii=False
                ) + "\n"
            )

    def filter(
            self,
            level: AuditLevel | None = None,
            client_id: str | None = None,
            action: str | None = None
    ):
        result = self.logs

        if level is not None:
            result = [
                log for log in result
                if log["level"] == level.value
            ]

        if client_id is not None:
            result = [
                log for log in result
                if log["client_id"] == client_id
            ]

        if action is not None:
            result = [
                log for log in result
                if log["action"] == action
            ]

        return result

    def get_all(self):
        return self.logs.copy()


class RiskAnalyzer:

    def __init__(
            self,
            large_amount_threshold:
            Decimal = Decimal("1000000"),
            frequent_operations_threshold: int = 5
    ):
        self.large_amount_threshold = (
            large_amount_threshold
        )

        self.frequent_operations_threshold = (
            frequent_operations_threshold
        )

    def analyze(
            self,
            transaction: Transaction,
            client_transactions: list[Transaction],
            new_account: bool = False
    ):
        risk_score = 0
        reasons = []

        if transaction.amount >= self.large_amount_threshold:
            risk_score += 2
            reasons.append("large_amount")

        if (
                len(client_transactions)
                >= self.frequent_operations_threshold
        ):
            risk_score += 2
            reasons.append("frequent_operations")

        if new_account:
            risk_score += 2
            reasons.append("new_account")

        if 0 <= transaction.created_at.hour < 5:
            risk_score += 2
            reasons.append("night_operation")

        if risk_score >= 5:
            level = RiskLevel.HIGH
        elif risk_score >= 2:
            level = RiskLevel.MEDIUM
        else:
            level = RiskLevel.LOW

        return {
            "transaction_id": transaction.transaction_id,
            "risk_level": level,
            "risk_score": risk_score,
            "reasons": reasons
        }

    def is_dangerous(self, risk_result: dict):
        return (
                risk_result["risk_level"]
                == RiskLevel.HIGH
        )

    def analyze_client(
            self,
            client_id: str,
            transactions: list[Transaction],
            client_account_ids: set[str]
    ):
        client_transactions = [
            transaction
            for transaction in transactions
            if (
                    transaction.sender in client_account_ids
                    or transaction.receiver in client_account_ids
            )
        ]

        high_risk = 0
        medium_risk = 0
        low_risk = 0

        for transaction in client_transactions:

            result = self.analyze(
                transaction,
                client_transactions
            )

            if result["risk_level"] == RiskLevel.HIGH:
                high_risk += 1

            elif result["risk_level"] == RiskLevel.MEDIUM:
                medium_risk += 1

            else:
                low_risk += 1

        return {
            "client_id": client_id,
            "total_transactions": len(
                client_transactions
            ),
            "high_risk": high_risk,
            "medium_risk": medium_risk,
            "low_risk": low_risk
        }


class ReportBuilder:

    def __init__(
            self,
            bank: Bank,
            transactions: list[Transaction],
            risk_analyzer: RiskAnalyzer
    ):
        self.bank = bank
        self.transactions = transactions
        self.risk_analyzer = risk_analyzer

    def client_report(self, client_id: str):
        client = self.bank.clients.get(client_id)

        if client is None:
            raise InvalidOperationError(
                "Client not found"
            )

        accounts = [
            self.bank.accounts[account_id]
            for account_id in client.accounts
            if account_id in self.bank.accounts
        ]

        transactions = [
            transaction
            for transaction in self.transactions
            if (
                    transaction.sender in client.accounts
                    or transaction.receiver in client.accounts
            )
        ]

        return {
            "client": str(client),

            "accounts": [
                account.get_account_info()
                for account in accounts
            ],

            "transactions": [
                self._transaction_to_dict(
                    transaction
                )
                for transaction in transactions
            ],

            "risk": self.risk_analyzer.analyze_client(
                client_id,
                self.transactions,
                client.accounts
            )
        }

    def bank_report(self):
        return {
            "clients": len(
                self.bank.clients
            ),
            "accounts": len(
                self.bank.accounts
            ),
            "transactions": len(
                self.transactions
            ),
            "total_balance":
                self.bank.get_total_balance(),
            "statistics":
                self.transaction_statistics()
        }

    def risk_report(self):
        results = []

        for transaction in self.transactions:
            result = self.risk_analyzer.analyze(
                transaction,
                self.transactions
            )

            results.append(result)

        return results

    def transaction_statistics(self):
        statistics = {
            "total": len(self.transactions),
            "pending": 0,
            "processing": 0,
            "completed": 0,
            "failed": 0,
            "cancelled": 0
        }

        for transaction in self.transactions:

            status = transaction.status

            if status == TransactionStatus.PENDING:
                statistics["pending"] += 1

            elif status == TransactionStatus.PROCESSING:
                statistics["processing"] += 1

            elif status == TransactionStatus.COMPLETED:
                statistics["completed"] += 1

            elif status == TransactionStatus.FAILED:
                statistics["failed"] += 1

            elif status == TransactionStatus.CANCELLED:
                statistics["cancelled"] += 1

        return statistics

    def export_to_json(
            self,
            data,
            file_path: str
    ):

        if not data:
            return

        Path(file_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
                file_path,
                "w",
                encoding="utf-8"
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
                default=str
            )

    def export_to_csv(
            self,
            data: dict,
            file_path: str
    ):
        if not data:
            return

        Path(file_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with open(
                file_path,
                "w",
                encoding="utf-8",
                newline=""
        ) as file:

            writer = csv.writer(file)

            writer.writerow(["metric", "value"])

            for key, value in data.items():
                writer.writerow([key, value])

    def save_charts(self, directory: str):
        Path(directory).mkdir(
            parents=True,
            exist_ok=True
        )

        self._save_client_balance_chart(directory)
        self._save_transaction_status_chart(directory)
        self._save_balance_movement_charts(directory)

    def _save_transaction_status_chart(
            self,
            directory
    ):
        statistics = self.transaction_statistics()

        labels = [
            "Completed",
            "Failed",
            "Cancelled",
            "Pending"
        ]

        values = [
            statistics["completed"],
            statistics["failed"],
            statistics["cancelled"],
            statistics["pending"]
        ]

        if sum(values) == 0:
            return

        plt.figure()

        plt.pie(
            values,
            labels=labels,
            autopct="%1.1f%%"
        )

        plt.title("Transaction Status")

        plt.savefig(
            f"{directory}/transaction_status.png"
        )

        plt.close()

    def _save_client_balance_chart(
            self,
            directory
    ):
        clients = list(
            self.bank.clients.values()
        )

        names = []
        balances = []

        for client in clients:

            balance = Decimal("0.00")

            for account_id in client.accounts:

                account = self.bank.accounts.get(
                    account_id
                )

                if account is None:
                    continue

                if isinstance(
                        account,
                        InvestmentAccount
                ):
                    balance += account.total_balance

                else:
                    balance += Decimal(
                        str(account.balance)
                    )

            names.append(client.client_id)
            balances.append(float(balance))

        if not names:
            return

        plt.figure()

        plt.bar(
            names,
            balances
        )

        plt.title("Client Balances")
        plt.xlabel("Client")
        plt.ylabel("Balance")
        plt.xticks(rotation=45)

        plt.tight_layout()

        plt.savefig(
            f"{directory}/client_balances.png"
        )

        plt.close()

    def _save_balance_movement_charts(
            self,
            directory
    ):
        for account_id, account in self.bank.accounts.items():

            balance_change = Decimal("0.00")
            points = []

            for transaction in self.transactions:

                if transaction.status != TransactionStatus.COMPLETED:
                    continue

                change = self._balance_change(
                    transaction,
                    account_id
                )

                if change == 0:
                    continue

                balance_change += change
                points.append(float(balance_change))

            if not points:
                continue

            plt.figure()

            plt.plot(
                range(1, len(points) + 1),
                points,
                marker="o"
            )

            plt.title(
                f"Balance movement: {account_id} "
                f"({account.currency.value})"
            )
            plt.xlabel("Operation")
            plt.ylabel("Cumulative change")

            plt.savefig(
                f"{directory}/balance_movement_{account_id}.png"
            )

            plt.close()

    @staticmethod
    def _balance_change(
            transaction: Transaction,
            account_id: str
    ) -> Decimal:
        change = Decimal("0.00")

        if (
                transaction.sender == account_id
                and transaction.debited_amount is not None
        ):
            change -= transaction.debited_amount

        if (
                transaction.receiver == account_id
                and transaction.credited_amount is not None
        ):
            change += transaction.credited_amount

        return change

    @staticmethod
    def _transaction_to_dict(
            transaction: Transaction
    ):
        return {
            "transaction_id":
                transaction.transaction_id,
            "type":
                transaction.transaction_type.value,
            "amount":
                transaction.amount,
            "currency":
                transaction.currency.value,
            "commission":
                transaction.commission,
            "sender":
                transaction.sender,
            "receiver":
                transaction.receiver,
            "status":
                transaction.status.value,
            "failure_reason":
                transaction.failure_reason,
            "created_at":
                transaction.created_at,
            "processed_at":
                transaction.processed_at
        }
