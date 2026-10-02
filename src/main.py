from src.models import (
    BankAccount,
    Currency,
    Status,
    AccountFrozenError,
    AccountClosedError,
    InvalidOperationError,
    InsufficientFundsError
)


def main():

    print("=" * 60)
    print("1. СОЗДАНИЕ СЧЕТОВ")
    print("=" * 60)

    # UUID должен сгенерироваться автоматически
    active_account = BankAccount(
        personal_info="Alexey",
        account_balance=10000,
        currency=Currency.RUB
    )

    frozen_account = BankAccount(
        personal_info="Ivan",
        account_balance=5000,
        account_status=Status.FROZEN,
        currency=Currency.USD
    )

    closed_account = BankAccount(
        personal_info="Petr",
        account_balance=2000,
        account_status=Status.CLOSED,
        currency=Currency.EUR
    )

    print(active_account)
    print(frozen_account)
    print(closed_account)

    print("\nСгенерированный ID:")
    print(active_account.account_id)


    print("\n" + "=" * 60)
    print("2. GET ACCOUNT INFO")
    print("=" * 60)

    print(active_account.get_account_info())


    print("\n" + "=" * 60)
    print("3. DEPOSIT")
    print("=" * 60)

    print("Баланс до пополнения:")
    print(active_account)

    active_account.deposit(5000)

    print("Баланс после пополнения на 5000:")
    print(active_account)


    print("\n" + "=" * 60)
    print("4. WITHDRAW")
    print("=" * 60)

    print("Баланс до снятия:")
    print(active_account)

    active_account.withdraw(3000)

    print("Баланс после снятия 3000:")
    print(active_account)


    print("\n" + "=" * 60)
    print("5. FROZEN ACCOUNT")
    print("=" * 60)

    try:
        frozen_account.deposit(1000)
    except AccountFrozenError as e:
        print(f"Deposit: {e}")

    try:
        frozen_account.withdraw(1000)
    except AccountFrozenError as e:
        print(f"Withdraw: {e}")


    print("\n" + "=" * 60)
    print("6. CLOSED ACCOUNT")
    print("=" * 60)

    try:
        closed_account.deposit(1000)
    except AccountClosedError as e:
        print(f"Deposit: {e}")

    try:
        closed_account.withdraw(1000)
    except AccountClosedError as e:
        print(f"Withdraw: {e}")


    print("\n" + "=" * 60)
    print("7. INVALID AMOUNT")
    print("=" * 60)

    try:
        active_account.deposit(-1000)
    except InvalidOperationError as e:
        print(f"Negative deposit: {e}")

    try:
        active_account.withdraw(-1000)
    except InvalidOperationError as e:
        print(f"Negative withdraw: {e}")

    try:
        active_account.deposit(0)
    except InvalidOperationError as e:
        print(f"Zero deposit: {e}")

    try:
        active_account.withdraw(0)
    except InvalidOperationError as e:
        print(f"Zero withdraw: {e}")


    print("\n" + "=" * 60)
    print("8. INVALID DATA TYPE")
    print("=" * 60)

    try:
        active_account.deposit("1000")
    except InvalidOperationError as e:
        print(f"String deposit: {e}")

    try:
        active_account.withdraw("1000")
    except InvalidOperationError as e:
        print(f"String withdraw: {e}")


    print("\n" + "=" * 60)
    print("9. INSUFFICIENT FUNDS")
    print("=" * 60)

    print("Текущий счёт:")
    print(active_account)

    try:
        active_account.withdraw(100000)
    except InsufficientFundsError as e:
        print(f"Withdraw: {e}")


    print("\n" + "=" * 60)
    print("10. ВАЛИДАЦИЯ СОЗДАНИЯ СЧЕТА")
    print("=" * 60)

    # Отрицательный начальный баланс
    try:
        BankAccount(
            personal_info="Test",
            account_balance=-100,
            currency=Currency.RUB
        )
    except InvalidOperationError as e:
        print(f"Negative balance: {e}")

    # Пустое имя клиента
    try:
        BankAccount(
            personal_info="",
            account_balance=1000,
            currency=Currency.RUB
        )
    except InvalidOperationError as e:
        print(f"Empty personal info: {e}")

    # Некорректная валюта
    try:
        BankAccount(
            personal_info="Test",
            account_balance=1000,
            currency="RUB"
        )
    except InvalidOperationError as e:
        print(f"Invalid currency: {e}")

    # Некорректный статус
    try:
        BankAccount(
            personal_info="Test",
            account_balance=1000,
            account_status="active"
        )
    except InvalidOperationError as e:
        print(f"Invalid status: {e}")


    print("\n" + "=" * 60)
    print("11. РАЗНЫЕ ВАЛЮТЫ")
    print("=" * 60)

    rub_account = BankAccount("Alexey", 1000, currency=Currency.RUB)
    usd_account = BankAccount("Alexey", 1000, currency=Currency.USD)
    eur_account = BankAccount("Alexey", 1000, currency=Currency.EUR)
    kzt_account = BankAccount("Alexey", 1000, currency=Currency.KZT)
    cny_account = BankAccount("Alexey", 1000, currency=Currency.CNY)

    print(rub_account)
    print(usd_account)
    print(eur_account)
    print(kzt_account)
    print(cny_account)


    print("\n" + "=" * 60)
    print("12. ФИНАЛЬНОЕ СОСТОЯНИЕ")
    print("=" * 60)

    print(active_account)
    print(active_account.get_account_info())


if __name__ == "__main__":
    main()
