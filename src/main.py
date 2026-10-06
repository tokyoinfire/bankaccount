import random
from collections import Counter
from datetime import datetime, time, timedelta
from decimal import Decimal
from pathlib import Path

from src.models import (
    BankAccount,
    SavingsAccount,
    PremiumAccount,
    InvestmentAccount,

    Client,
    Bank,

    Currency,
    Status,
    AccountType,
    AssetType,
    TransactionType,
    TransactionStatus,
    AuditLevel,
    RiskLevel,

    Transaction,
    TransactionQueue,
    TransactionProcessor,

    AuditLog,
    RiskAnalyzer,
    ReportBuilder,

    AccountFrozenError,
    AccountClosedError,
    InvalidOperationError,
    InsufficientFundsError,
)


def section(title: str):
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)


def main():


    section("1. СОЗДАНИЕ ОБЫЧНЫХ СЧЕТОВ")

    active_account = BankAccount(
        personal_info="Alexey",
        account_balance=10000,
        currency=Currency.RUB,
    )

    frozen_account = BankAccount(
        personal_info="Ivan",
        account_balance=5000,
        account_status=Status.FROZEN,
        currency=Currency.USD,
    )

    closed_account = BankAccount(
        personal_info="Petr",
        account_balance=2000,
        account_status=Status.CLOSED,
        currency=Currency.EUR,
    )

    print(active_account)
    print(frozen_account)
    print(closed_account)

    print("\nСгенерированный UUID:")
    print(active_account.account_id)



    section("2. GET ACCOUNT INFO")

    print(active_account.get_account_info())


    section("3. DEPOSIT")

    print("До:", active_account)

    active_account.deposit(5000)

    print("После deposit(5000):", active_account)



    section("4. WITHDRAW")

    print("До:", active_account)

    active_account.withdraw(3000)

    print("После withdraw(3000):", active_account)



    section("5. FROZEN ACCOUNT")

    try:
        frozen_account.deposit(1000)
    except AccountFrozenError as e:
        print(f"Deposit запрещён: {e}")

    try:
        frozen_account.withdraw(1000)
    except AccountFrozenError as e:
        print(f"Withdraw запрещён: {e}")



    section("6. CLOSED ACCOUNT")

    try:
        closed_account.deposit(1000)
    except AccountClosedError as e:
        print(f"Deposit запрещён: {e}")

    try:
        closed_account.withdraw(1000)
    except AccountClosedError as e:
        print(f"Withdraw запрещён: {e}")


    section("7. НЕКОРРЕКТНАЯ СУММА")

    for operation in (
        lambda: active_account.deposit(-1000),
        lambda: active_account.withdraw(-1000),
        lambda: active_account.deposit(0),
        lambda: active_account.withdraw(0),
    ):
        try:
            operation()
        except InvalidOperationError as e:
            print(f"Ошибка: {e}")



    section("8. НЕКОРРЕКТНЫЙ ТИП ДАННЫХ")

    try:
        active_account.deposit("1000")
    except InvalidOperationError as e:
        print(f"String deposit: {e}")

    try:
        active_account.withdraw("1000")
    except InvalidOperationError as e:
        print(f"String withdraw: {e}")



    section("9. НЕДОСТАТОЧНО СРЕДСТВ")

    print("Баланс:", active_account)

    try:
        active_account.withdraw(100000)
    except InsufficientFundsError as e:
        print(f"Ошибка: {e}")



    section("10. ВАЛИДАЦИЯ СОЗДАНИЯ СЧЁТА")

    try:
        BankAccount(
            personal_info="Test",
            account_balance=-100,
            currency=Currency.RUB,
        )
    except InvalidOperationError as e:
        print(f"Negative balance: {e}")

    try:
        BankAccount(
            personal_info="",
            account_balance=1000,
            currency=Currency.RUB,
        )
    except InvalidOperationError as e:
        print(f"Empty personal info: {e}")

    try:
        BankAccount(
            personal_info="Test",
            account_balance=1000,
            currency="RUB",
        )
    except InvalidOperationError as e:
        print(f"Invalid currency: {e}")

    try:
        BankAccount(
            personal_info="Test",
            account_balance=1000,
            account_status="active",
        )
    except InvalidOperationError as e:
        print(f"Invalid status: {e}")



    section("11. РАЗНЫЕ ВАЛЮТЫ")

    rub_account = BankAccount(
        personal_info="Alexey",
        account_balance=1000,
        currency=Currency.RUB,
    )

    usd_account = BankAccount(
        personal_info="Alexey",
        account_balance=1000,
        currency=Currency.USD,
    )

    eur_account = BankAccount(
        personal_info="Alexey",
        account_balance=1000,
        currency=Currency.EUR,
    )

    kzt_account = BankAccount(
        personal_info="Alexey",
        account_balance=1000,
        currency=Currency.KZT,
    )

    cny_account = BankAccount(
        personal_info="Alexey",
        account_balance=1000,
        currency=Currency.CNY,
    )

    print(rub_account)
    print(usd_account)
    print(eur_account)
    print(kzt_account)
    print(cny_account)



    section("12. SAVINGS ACCOUNT")

    savings_account = SavingsAccount(
        personal_info="Alexey",
        account_balance=10000,
        currency=Currency.RUB,
        min_balance=5000,
        monthly_interest_rate=Decimal("0.05"),
    )

    print("До начисления процентов:")
    print(savings_account)

    savings_account.apply_monthly_interest()

    print("После начисления 5%:")
    print(savings_account)

    print("Информация:")
    print(savings_account.get_account_info())


    try:
        savings_account.withdraw(6000)
    except InsufficientFundsError as e:
        print(f"Нарушение минимального остатка: {e}")



    section("13. PREMIUM ACCOUNT")

    premium_account = PremiumAccount(
        personal_info="Alexey",
        account_balance=20000,
        currency=Currency.RUB,
        overdraft_limit=Decimal("1000"),
        commission=Decimal("2.00"),
    )

    print("Начальное состояние:")
    print(premium_account)

    premium_account.withdraw(500)

    print("После withdraw(500) с комиссией:")
    print(premium_account)

    premium_account.withdraw(20000)

    print("После withdraw(20000) в пределах овердрафта:")
    print(premium_account)

    try:
        premium_account.withdraw(25000)
    except InsufficientFundsError as e:
        print(f"Превышение овердрафта: {e}")

    section("14. INVESTMENT ACCOUNT")

    investment_account = InvestmentAccount(
        personal_info="Alexey",
        account_balance=100000,
        currency=Currency.RUB,
    )

    print("Начальное состояние:")
    print(investment_account)

    print("\nПополняем портфель:")

    investment_account.buy_asset(
        AssetType.STOCKS,
        Decimal("30000"),
    )

    investment_account.buy_asset(
        AssetType.BONDS,
        Decimal("20000"),
    )

    investment_account.buy_asset(
        AssetType.ETF,
        Decimal("10000"),
    )

    print(investment_account)

    print("\nРаспределение портфеля:")
    print(investment_account.portfolio_distribution)

    print("\nВыводим 5000 из STOCKS:")

    investment_account.sell_asset(
        AssetType.STOCKS,
        Decimal("5000"),
    )

    print(investment_account)

    print("\nОбычное пополнение и снятие свободных средств:")

    investment_account.deposit(15000)
    investment_account.withdraw(Decimal("2500"))

    print(investment_account)

    print("\nПрогноз роста портфеля:")

    growth_rates = {
        AssetType.STOCKS: Decimal("0.10"),
        AssetType.BONDS: Decimal("0.04"),
        AssetType.ETF: Decimal("0.07"),
    }

    expected_growth = investment_account.project_yearly_growth(
        growth_rates
    )

    print(expected_growth)

    print("\nПроверка недостатка средств:")

    try:
        investment_account.sell_asset(
            AssetType.STOCKS,
            Decimal("1000000"),
        )
    except InsufficientFundsError as e:
        print(f"Ошибка: {e}")


    section("15. CLIENT")

    client = Client(
        client_id="client-001",
        personal_info="Alexey Veklenko",
        status=Status.ACTIVE,
        accounts=set(),
        contacts={
            "email": "alexey@example.com",
            "phone": "+79990000000",
        },
        age=20,
        password="password123",
    )

    print(client)

    client.add_account(active_account.account_id)

    print("\nПосле добавления счёта:")
    print(client)

    client.remove_account(active_account.account_id)

    print("\nПосле удаления счёта:")
    print(client)

    client.add_account(active_account.account_id)


    section("16. ВАЛИДАЦИЯ CLIENT")

    try:
        Client(
            client_id="client-002",
            personal_info="Test",
            status=Status.ACTIVE,
            accounts=set(),
            contacts={},
            age=17,
            password="password",
        )
    except InvalidOperationError as e:
        print(f"Возраст < 18: {e}")


    section("17. BANK")

    bank = Bank()

    bank.add_client(client)

    print("Клиенты банка:")
    print(bank.clients)



    section("18. OPEN ACCOUNT")

    new_account = BankAccount(
        personal_info="Alexey Dmitriev",
        account_balance=25000,
        currency=Currency.RUB,
    )

    bank.open_account(
        client_id=client.client_id,
        account=new_account,
    )

    print("Новый счёт:")
    print(new_account)

    print("\nСчета клиента:")
    print(client.accounts)


    section("19. АУТЕНТИФИКАЦИЯ")

    authenticated_client = bank.authenticate_client(
        client.client_id,
        "password123",
    )

    print("Успешная авторизация:")
    print(authenticated_client)


    print("\nПроверка неверного пароля:")

    for attempt in range(1, 4):
        try:
            bank.authenticate_client(
                client.client_id,
                "wrong-password",
            )
        except InvalidOperationError as e:
            print(f"Попытка {attempt}: {e}")


    section("20. БЛОКИРОВКА ПОСЛЕ 3 НЕВЕРНЫХ ПАРОЛЕЙ")

    print("Заблокирован:", client.is_blocked)
    print("Неудачных попыток:", client.failed_attempts)


    section("21. ОПЕРАЦИИ ЧЕРЕЗ BANK")

    client2 = Client(
        client_id="client-002",
        personal_info="Ivan Ivanov",
        status=Status.ACTIVE,
        accounts=set(),
        contacts={
            "email": "ivan@example.com",
        },
        age=25,
        password="ivan-password",
    )

    bank.add_client(client2)

    account2 = BankAccount(
        personal_info="Ivan Ivanov",
        account_balance=10000,
        currency=Currency.RUB,
    )

    bank.open_account(
        client_id=client2.client_id,
        account=account2,
    )

    print("До операции:")
    print(account2)

    bank.deposit(
        client_id=client2.client_id,
        account_id=account2.account_id,
        amount=5000,
        password="ivan-password",
    )

    print("После deposit:")
    print(account2)

    bank.withdraw(
        client_id=client2.client_id,
        account_id=account2.account_id,
        amount=2000,
        password="ivan-password",
    )

    print("После withdraw:")
    print(account2)

    section("22. ПРОВЕРКА ВЛАДЕЛЬЦА СЧЁТА")

    try:
        bank.withdraw(
            client_id=client2.client_id,
            account_id=active_account.account_id,
            amount=100,
            password="ivan-password",
        )
    except InvalidOperationError as e:
        print(f"Операция над чужим счётом запрещена: {e}")



    section("23. FREEZE / UNFREEZE ACCOUNT")

    bank.freeze_account(
        client_id=client2.client_id,
        account_id=account2.account_id,
        password="ivan-password",
    )

    print("После freeze:")
    print(account2)

    try:
        bank.deposit(
            client_id=client2.client_id,
            account_id=account2.account_id,
            amount=1000,
            password="ivan-password",
        )
    except AccountFrozenError as e:
        print(f"Операция после freeze запрещена: {e}")

    bank.unfreeze_account(
        client_id=client2.client_id,
        account_id=account2.account_id,
        password="ivan-password",
    )

    print("После unfreeze:")
    print(account2)


    section("24. SEARCH ACCOUNTS")

    accounts = bank.search_accounts(
        client_id=client2.client_id,
    )

    for account in accounts:
        print(account)


    section("25. CLOSE ACCOUNT")

    bank.close_account(
        client_id=client2.client_id,
        account_id=account2.account_id,
        password="ivan-password",
    )

    print("После закрытия:")
    print(account2)


    section("26. TRANSACTION")

    transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("1000"),
        currency=Currency.RUB,
        sender=active_account.account_id,
        receiver=account2.account_id,
    )

    print(transaction)

    print("Статус:", transaction.status)

    transaction.mark_processing()

    print("После mark_processing:", transaction.status)

    transaction.mark_completed()

    print("После mark_completed:", transaction.status)


    section("27. FAILED TRANSACTION")

    failed_transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("1000"),
        currency=Currency.RUB,
        sender=active_account.account_id,
        receiver=account2.account_id,
    )

    failed_transaction.mark_processing()

    failed_transaction.mark_failed(
        "Insufficient funds"
    )

    print(failed_transaction)
    print("Статус:", failed_transaction.status)
    print("Причина:", failed_transaction.failure_reason)


    section("28. CANCEL TRANSACTION")

    cancelled_transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("500"),
        currency=Currency.RUB,
        sender=active_account.account_id,
        receiver=account2.account_id,
    )

    cancelled_transaction.cancel()

    print(cancelled_transaction)
    print("Статус:", cancelled_transaction.status)


    section("29. TRANSACTION QUEUE")

    queue = TransactionQueue()

    queued_transaction_1 = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("100"),
        currency=Currency.RUB,
        sender=active_account.account_id,
        receiver=new_account.account_id,
    )

    queued_transaction_2 = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("200"),
        currency=Currency.RUB,
        sender=active_account.account_id,
        receiver=new_account.account_id,
    )

    queue.add(
        queued_transaction_1,
        priority=1,
    )

    queue.add(
        queued_transaction_2,
        priority=10,
    )

    print("Очередь создана.")

    next_transaction = queue.pop()

    if next_transaction:
        print("Следующая транзакция:")
        print(next_transaction)


    section("30. ОТМЕНА ТРАНЗАКЦИИ В ОЧЕРЕДИ")

    transaction_to_cancel = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("300"),
        currency=Currency.RUB,
        sender=active_account.account_id,
        receiver=new_account.account_id,
    )

    queue.add(
        transaction_to_cancel,
        priority=5,
    )

    cancelled = queue.cancel(
        transaction_to_cancel.transaction_id
    )

    print("Отмена успешна:", cancelled)


    section("31. TRANSACTION PROCESSOR")

    processor = TransactionProcessor(
        bank=bank,
    )

    sender = BankAccount(
        personal_info="Sender",
        account_balance=10000,
        currency=Currency.RUB,
    )

    receiver = BankAccount(
        personal_info="Receiver",
        account_balance=1000,
        currency=Currency.RUB,
    )

    bank_account_client = Client(
        client_id="client-003",
        personal_info="Sender",
        status=Status.ACTIVE,
        accounts=set(),
        contacts={},
        age=30,
        password="sender-password",
    )

    bank.add_client(bank_account_client)

    bank.open_account(
        client_id=bank_account_client.client_id,
        account=sender,
    )

    bank.open_account(
        client_id=bank_account_client.client_id,
        account=receiver,
    )

    transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("1000"),
        currency=Currency.RUB,
        sender=sender.account_id,
        receiver=receiver.account_id,
    )

    print("До обработки:")
    print(sender)
    print(receiver)

    try:
        processor.process(transaction)

        print("\nПосле обработки:")
        print(sender)
        print(receiver)

        print("\nСтатус транзакции:")
        print(transaction.status)

    except InvalidOperationError as e:
        print(f"Ошибка обработки: {e}")


    section("32. КОНВЕРТАЦИЯ ВАЛЮТ")

    exchange_rates = {
        (Currency.RUB, Currency.USD): Decimal("0.011"),
        (Currency.USD, Currency.RUB): Decimal("90"),
        (Currency.RUB, Currency.EUR): Decimal("0.010"),
        (Currency.EUR, Currency.RUB): Decimal("100"),
    }

    processor.exchange_rates = exchange_rates

    converted = processor.convert_currency(
        Decimal("9000"),
        Currency.RUB,
        Currency.USD,
        exchange_rates
    )

    print("9000 RUB -> USD:")
    print(converted)


    section("33. AUDIT LOG")

    audit_log = AuditLog()

    audit_log.log(
        level=AuditLevel.INFO,
        action="LOGIN",
        message="Client successfully authenticated",
        client_id=client2.client_id,
    )

    audit_log.log(
        level=AuditLevel.WARNING,
        action="LOGIN_FAILED",
        message="Invalid password",
        client_id=client2.client_id,
    )

    audit_log.log(
        level=AuditLevel.CRITICAL,
        action="ACCOUNT_FREEZE",
        message="Account was frozen",
        client_id=client2.client_id,
    )

    print("Все записи:")
    for log in audit_log.get_all():
        print(log)

    print("\nWARNING:")
    for log in audit_log.filter(
        level=AuditLevel.WARNING
    ):
        print(log)


    section("34. RISK ANALYZER")

    risk_analyzer = RiskAnalyzer(
        large_amount_threshold=Decimal("100000"),
        frequent_operations_threshold=5,
    )

    risk_transaction = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("500000"),
        currency=Currency.RUB,
        sender=sender.account_id,
        receiver=receiver.account_id,
    )

    risk = risk_analyzer.analyze(
        transaction=risk_transaction,
        client_transactions=[
            risk_transaction,
            transaction,
            failed_transaction,
            cancelled_transaction,
            queued_transaction_1,
        ],
    )

    print("Risk level:")
    print(risk)

    print("Dangerous:")
    print(risk_analyzer.is_dangerous(risk))


    section("35. CLIENT RISK ANALYSIS")

    client_transactions = [
        transaction,
        failed_transaction,
        cancelled_transaction,
        risk_transaction,
    ]

    client_risk = risk_analyzer.analyze_client(
        client_id=client2.client_id,
        transactions=client_transactions,
        client_account_ids=client2.accounts,
    )

    print(client_risk)


    section("36. TOTAL BANK BALANCE")

    total_balance = bank.get_total_balance()

    print("Общий баланс банка:")
    print(total_balance)


    section("37. CLIENTS RANKING")

    ranking = bank.get_clients_ranking()

    for index, ranked_client in enumerate(ranking, start=1):
        print(
            f"{index}. "
            f"{ranked_client.client_id} "
            f"- {ranked_client.personal_info}"
        )


    section("38. REPORT BUILDER")

    transactions = [
        transaction,
        failed_transaction,
        cancelled_transaction,
        risk_transaction,
    ]

    report_builder = ReportBuilder(
        bank=bank,
        transactions=transactions,
        risk_analyzer=risk_analyzer,
    )

    print("\nClient report:")
    print(
        report_builder.client_report(
            client2.client_id
        )
    )

    print("\nBank report:")
    print(
        report_builder.bank_report()
    )

    print("\nRisk report:")
    print(
        report_builder.risk_report()
    )

    print("\nTransaction statistics:")
    print(
        report_builder.transaction_statistics()
    )


    section("39. EXPORT REPORTS")

    report_builder.export_to_json(
        report_builder.bank_report(),
        "reports/bank_report.json"
    )

    report_builder.export_to_csv(
        report_builder.transaction_statistics(),
        "reports/transactions.csv"
    )

    print("JSON отчёт сохранён.")
    print("CSV отчёт сохранён.")


    section("40. СОХРАНЕНИЕ ГРАФИКОВ")

    report_builder.save_charts(
        "reports/charts"
    )

    print("Графики сохранены.")


    section("41. ФИНАЛЬНОЕ СОСТОЯНИЕ")

    print("\nActive account:")
    print(active_account)

    print("\nSavings account:")
    print(savings_account)

    print("\nPremium account:")
    print(premium_account)

    print("\nInvestment account:")
    print(investment_account)

    print("\nClient:")
    print(client)

    print("\nBank total balance:")
    print(bank.get_total_balance())


def describe_result(transaction):
    if transaction.status == TransactionStatus.COMPLETED:
        return "ИСПОЛНЕНА"

    reason = transaction.failure_reason or ""

    if reason.startswith("Blocked"):
        return "ОТКЛОНЕНА (высокий риск)"

    return f"ОШИБКА: {reason}"


def run_simulation():
    section("42. СИМУЛЯЦИЯ РАБОТЫ БАНКА")

    rng = random.Random(42)

    audit_path = Path("data/audit.jsonl")
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    audit_path.unlink(missing_ok=True)

    audit_log = AuditLog(file_path=str(audit_path))
    bank = Bank(audit_log=audit_log)

    processor = TransactionProcessor(
        bank=bank,
        external_transfer_commission=Decimal("0.01"),
        max_retries=3,
        exchange_rates={
            (Currency.RUB, Currency.USD): Decimal("0.011"),
            (Currency.USD, Currency.RUB): Decimal("90"),
            (Currency.RUB, Currency.EUR): Decimal("0.010"),
            (Currency.EUR, Currency.RUB): Decimal("100"),
            (Currency.USD, Currency.EUR): Decimal("0.92"),
            (Currency.EUR, Currency.USD): Decimal("1.09"),
        },
        risk_analyzer=RiskAnalyzer(
            large_amount_threshold=Decimal("100000"),
            frequent_operations_threshold=4,
        ),
        audit_log=audit_log,
    )

    print("Клиенты банка:")
    clients = (
        ("client-101", "Иван Петров", 34, "pass-101"),
        ("client-102", "Мария Смирнова", 28, "pass-102"),
        ("client-103", "Алексей Волков", 41, "pass-103"),
        ("client-104", "Ольга Кузнецова", 25, "pass-104"),
        ("client-105", "Дмитрий Соколов", 52, "pass-105"),
        ("client-106", "Анна Попова", 37, "pass-106"),
        ("client-107", "Сергей Лебедев", 30, "pass-107"),
        ("client-108", "Елена Морозова", 45, "pass-108"),
    )

    for client_id, name, age, password in clients:
        bank.add_client(
            Client(
                client_id=client_id,
                personal_info=name,
                status=Status.ACTIVE,
                accounts=set(),
                contacts={"email": f"{client_id}@example.com"},
                age=age,
                password=password,
            )
        )
        print(f"  {client_id} {name}")

    accounts = [
        ("client-101", BankAccount(
            personal_info="Иван Петров",
            account_balance=150000,
            currency=Currency.RUB,
        )),
        ("client-101", SavingsAccount(
            personal_info="Иван Петров",
            account_balance=300000,
            currency=Currency.RUB,
            min_balance=10000,
            monthly_interest_rate=Decimal("0.01"),
        )),
        ("client-102", BankAccount(
            personal_info="Мария Смирнова",
            account_balance=80000,
            currency=Currency.RUB,
        )),
        ("client-102", BankAccount(
            personal_info="Мария Смирнова",
            account_balance=2000,
            currency=Currency.USD,
        )),
        ("client-103", PremiumAccount(
            personal_info="Алексей Волков",
            account_balance=50000,
            currency=Currency.RUB,
            overdraft_limit=Decimal("20000"),
            commission=Decimal("2.00"),
        )),
        ("client-104", BankAccount(
            personal_info="Ольга Кузнецова",
            account_balance=25000,
            currency=Currency.RUB,
        )),
        ("client-104", BankAccount(
            personal_info="Ольга Кузнецова",
            account_balance=800,
            currency=Currency.EUR,
        )),
        ("client-105", SavingsAccount(
            personal_info="Дмитрий Соколов",
            account_balance=40000,
            currency=Currency.EUR,
            min_balance=5000,
            monthly_interest_rate=Decimal("0.005"),
        )),
        ("client-106", PremiumAccount(
            personal_info="Анна Попова",
            account_balance=5000,
            currency=Currency.USD,
            overdraft_limit=Decimal("500"),
            commission=Decimal("1.00"),
        )),
        ("client-107", BankAccount(
            personal_info="Сергей Лебедев",
            account_balance=12000,
            currency=Currency.RUB,
        )),
        ("client-108", BankAccount(
            personal_info="Елена Морозова",
            account_balance=60000,
            currency=Currency.RUB,
        )),
        ("client-108", InvestmentAccount(
            personal_info="Елена Морозова",
            account_balance=100000,
            currency=Currency.RUB,
        )),
    ]

    for client_id, account in accounts:
        bank.open_account(client_id=client_id, account=account)

    investment_account = accounts[-1][1]
    investment_account.buy_asset(AssetType.STOCKS, Decimal("30000"))
    investment_account.buy_asset(AssetType.BONDS, Decimal("20000"))

    new_account = BankAccount(
        personal_info="Мария Смирнова",
        account_balance=0,
        currency=Currency.RUB,
    )
    bank.open_account(client_id="client-102", account=new_account)

    print(f"\nСчетов открыто: {len(accounts)}")

    for _ in range(3):
        try:
            bank.authenticate_client("client-106", "wrong-password")
        except InvalidOperationError:
            pass

    print(
        "Клиент client-106 заблокирован после 3 неверных паролей: "
        f"{bank.clients['client-106'].is_blocked}"
    )

    section("43. ГЕНЕРАЦИЯ ТРАНЗАКЦИЙ И ОЧЕРЕДЬ")

    usable = [account for _, account in accounts]

    transactions = []

    for _ in range(40):
        kind = rng.choices(
            [
                TransactionType.TRANSFER,
                TransactionType.DEPOSIT,
                TransactionType.WITHDRAW,
            ],
            weights=[6, 2, 2],
        )[0]

        source = rng.choice(usable)
        target = rng.choice(
            [account for account in usable if account is not source]
        )

        amount = Decimal(rng.randint(100, 20000))

        if rng.random() < 0.1:
            amount = Decimal(rng.randint(150000, 400000))

        if kind == TransactionType.TRANSFER:
            transaction = Transaction(
                transaction_type=kind,
                amount=amount,
                currency=source.currency,
                sender=source.account_id,
                receiver=target.account_id,
                is_external=rng.random() < 0.3,
            )

        elif kind == TransactionType.DEPOSIT:
            transaction = Transaction(
                transaction_type=kind,
                amount=amount,
                currency=target.currency,
                receiver=target.account_id,
            )

        else:
            transaction = Transaction(
                transaction_type=kind,
                amount=amount,
                currency=source.currency,
                sender=source.account_id,
            )

        transactions.append(transaction)

    bank.freeze_account(
        client_id="client-107",
        account_id=accounts[9][1].account_id,
        password="pass-107",
    )

    bank.close_account(
        client_id="client-104",
        account_id=accounts[6][1].account_id,
        password="pass-104",
    )

    print("Счёт client-107 заморожен, счёт client-104 (EUR) закрыт.\n")

    queue = TransactionQueue()
    now = datetime.now()

    for transaction in transactions:
        priority = rng.choice([0, 1, 5, 10])
        delayed = rng.random() < 0.15
        execute_at = now + timedelta(hours=2) if delayed else None

        queue.add(
            transaction,
            priority=priority,
            execute_at=execute_at,
        )

        note = f", отложена до {execute_at:%H:%M}" if delayed else ""

        print(
            f"  В очередь: {transaction.transaction_id} "
            f"{transaction.transaction_type.value} "
            f"{transaction.amount} {transaction.currency.value} "
            f"priority={priority}{note}"
        )

    cancelled_transaction = transactions[-1]
    queue.cancel(cancelled_transaction.transaction_id)

    print(f"\nОтменена в очереди: {cancelled_transaction.transaction_id}")

    suspicious_transfer = Transaction(
        transaction_type=TransactionType.TRANSFER,
        amount=Decimal("250000"),
        currency=Currency.RUB,
        sender=accounts[0][1].account_id,
        receiver=new_account.account_id,
    )
    transactions.append(suspicious_transfer)
    queue.add(suspicious_transfer, priority=0)

    print(
        f"  В очередь (крупный перевод на новый счёт): "
        f"{suspicious_transfer.transaction_id} "
        f"{suspicious_transfer.amount} {suspicious_transfer.currency.value}"
    )

    section("44. ИСПОЛНЕНИЕ ОЧЕРЕДИ")

    processed = processor.process_queue(queue)

    for transaction in processed:
        print(
            f"  {transaction.transaction_id} "
            f"{transaction.transaction_type.value:8} "
            f"{transaction.amount:>10} {transaction.currency.value}: "
            f"{describe_result(transaction)}"
        )

    print(f"\nОсталось в очереди (отложенные): {len(queue)}")

    print("\nОперации очереди с инвестиционным счётом:")
    for transaction in processed:
        if investment_account.account_id in (
                transaction.sender,
                transaction.receiver
        ):
            print(
                f"  {transaction.transaction_id} "
                f"{transaction.transaction_type.value:8} "
                f"{transaction.amount:>10} {transaction.currency.value}: "
                f"{describe_result(transaction)}"
            )

    print(investment_account)

    section("45. ПОЛЬЗОВАТЕЛЬСКИЕ СЦЕНАРИИ")

    client_id = "client-101"
    user_accounts = bank.search_accounts(client_id=client_id)

    print(f"Счета клиента {client_id}:")
    for account in user_accounts:
        print(account)

    user_account_ids = {account.account_id for account in user_accounts}

    history = [
        transaction
        for transaction in transactions
        if (
                transaction.sender in user_account_ids
                or transaction.receiver in user_account_ids
        )
    ]

    print(f"\nИстория операций клиента {client_id}: {len(history)}")
    for transaction in history:
        print(
            f"  {transaction.transaction_id} "
            f"{transaction.transaction_type.value} "
            f"{transaction.amount} {transaction.currency.value} "
            f"-> {transaction.status.value}"
        )

    suspicious = [
        transaction
        for transaction in transactions
        if transaction.risk_level in (RiskLevel.MEDIUM, RiskLevel.HIGH)
    ]

    print(f"\nПодозрительные операции (MEDIUM/HIGH): {len(suspicious)}")
    for transaction in suspicious:
        print(
            f"  {transaction.transaction_id} "
            f"risk={transaction.risk_level.value} "
            f"status={transaction.status.value}"
        )

    section("46. БАНК: РИСК-ПРОВЕРКА ПРЯМЫХ ОПЕРАЦИЙ")

    owner_id = "client-103"
    owner_password = "pass-103"
    owner_account = accounts[4][1]

    for _ in range(5):
        bank.deposit(
            client_id=owner_id,
            account_id=owner_account.account_id,
            password=owner_password,
            amount=100,
        )

    fresh_account = BankAccount(
        personal_info="Алексей Волков",
        account_balance=0,
        currency=Currency.RUB,
    )
    bank.open_account(client_id=owner_id, account=fresh_account)

    print("Пять небольших пополнений выполнены.")

    try:
        bank.deposit(
            client_id=owner_id,
            account_id=fresh_account.account_id,
            password=owner_password,
            amount=1500000,
        )
        print("Крупное пополнение нового счёта исполнено.")
    except InvalidOperationError as error:
        print(f"Крупное пополнение нового счёта заблокировано банком: {error}")

    # Фактор new_account относится только к переводам, поэтому
    # пополнение получает максимум MEDIUM и банком не блокируется
    last_risk = bank.history[-1].risk
    print(
        f"Риск операции: {last_risk['risk_level'].value} "
        f"({', '.join(last_risk['reasons'])})"
    )
    print(f"Баланс нового счёта: {fresh_account.balance}")
    print(f"Операций в истории банка: {len(bank.history)}")

    section("47. ОТЧЁТЫ")

    report_builder = ReportBuilder(
        bank=bank,
        transactions=transactions,
        risk_analyzer=processor.risk_analyzer,
    )

    print("Топ-3 клиента по балансу:")
    for index, ranked in enumerate(
            bank.get_clients_ranking()[:3],
            start=1
    ):
        print(f"  {index}. {ranked.client_id} - {ranked.personal_info}")

    print("\nСтатистика транзакций:")
    print(report_builder.transaction_statistics())

    print("\nОшибки исполнения:")
    reasons = Counter(
        transaction.failure_reason
        for transaction in transactions
        if transaction.status == TransactionStatus.FAILED
    )
    for reason, count in reasons.most_common():
        print(f"  {count} x {reason}")

    print("\nСобытия аудита по уровням:")
    print(Counter(log["level"] for log in audit_log.get_all()))

    print(
        "\nОбщий баланс банка (суммы без конвертации валют): "
        f"{bank.get_total_balance()}"
    )

    report_builder.export_to_json(
        report_builder.bank_report(),
        "reports/simulation_bank_report.json",
    )
    report_builder.export_to_csv(
        report_builder.transaction_statistics(),
        "reports/simulation_transactions.csv",
    )
    report_builder.save_charts("reports/charts")

    print("\nОтчёты и графики сохранены в reports/.")


if __name__ == "__main__":
    main()
    run_simulation()