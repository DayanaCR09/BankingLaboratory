import logging
from datetime import UTC, date, datetime
from io import StringIO

import pytest

from src.banking import BankAccount, Customer, InsufficientFundsError


def test_account_constructor_and_logging() -> None:
    stream = StringIO()
    root_logger = logging.getLogger()
    previous_handlers = root_logger.handlers[:]
    previous_level = root_logger.level

    root_logger.handlers.clear()
    root_logger.setLevel(logging.INFO)
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    root_logger.addHandler(handler)

    try:
        account = BankAccount("12345", "USD", "checking", 100.0)
        assert account.account_number == "12345"
        assert account.currency == "USD"
        assert account._account_type == "checking"
        assert account.balance == 100.0

        account.deposit(50.0)
        try:
            account.withdraw(300.0)
        except InsufficientFundsError as exc:
            assert exc.attempted_amount == 300.0
            assert "Insufficient funds" in str(exc)
        output = stream.getvalue()
    finally:
        root_logger.handlers = previous_handlers
        root_logger.setLevel(previous_level)

    assert "INFO" in output
    assert "ERROR" in output
    assert "Deposited" in output
    assert "Insufficient funds" in output


def test_negative_amounts_raise_value_error() -> None:
    account = BankAccount("A1", "USD", "checking", 100.0)

    with pytest.raises(ValueError):
        account.deposit(-1.0)

    with pytest.raises(ValueError):
        account.withdraw(-1.0)


def test_savings_account_cannot_drop_below_minimum() -> None:
    account = BankAccount("S1", "USD", "savings", 100.0)

    with pytest.raises(InsufficientFundsError):
        account.withdraw(1.0)

    assert account.balance == 100.0


def test_convert_currency_valid_and_invalid_rate() -> None:
    account = BankAccount("C1", "USD", "checking", 100.0)

    converted = account.convert_currency("EUR", 0.9)
    assert converted == 90.0

    with pytest.raises(ValueError):
        account.convert_currency("EUR", 0)

    with pytest.raises(ValueError):
        account.convert_currency("EUR", -1)


def test_create_savings_uses_default_type_and_validates_minimum_balance() -> None:
    account = BankAccount.create_savings("SAV1", "USD")
    assert account._account_type == "savings"
    assert account.balance == 100.0

    with pytest.raises(ValueError):
        BankAccount.create_savings("BAD", "USD", initial_balance=99.99)


def test_is_valid_account_number_requires_exactly_ten_digits() -> None:
    assert BankAccount.is_valid_account_number("1234567890") is True
    assert BankAccount.is_valid_account_number("123456789") is False
    assert BankAccount.is_valid_account_number("12345a7890") is False
    assert BankAccount.is_valid_account_number("") is False


def test_customer_requires_adult_age_and_assigns_consecutive_ids() -> None:
    Customer.user_count = 0

    adult = Customer("Alice", date(1990, 1, 1))
    assert adult.user_id == 1
    assert adult.name == "Alice"
    assert adult.accounts == []

    with pytest.raises(ValueError):
        Customer("Bob", datetime.now(UTC).date())

    with pytest.raises(ValueError):
        Customer("Teen", date(2010, 1, 1))


def test_customer_add_account_rejects_invalid_account_number() -> None:
    customer = Customer("Alice", date(1990, 1, 1))
    invalid_account = BankAccount("123", "USD", "checking", 50.0)

    customer.add_account(invalid_account)

    assert customer.accounts == []


def test_customer_get_total_balance_sums_all_accounts() -> None:
    customer = Customer("Alice", date(1990, 1, 1))
    customer.add_account(BankAccount("1234567890", "USD", "checking", 100.0))
    customer.add_account(BankAccount("1234567891", "USD", "checking", 250.0))

    assert customer.get_total_balance() == 350.0


def test_customer_transfer_validates_account_type_rules() -> None:
    customer = Customer("Alice", date(1990, 1, 1))
    source = BankAccount("1234567890", "USD", "checking", 200.0)
    target = BankAccount("1234567891", "USD", "savings", 150.0)
    customer.add_account(source)
    customer.add_account(target)

    result = customer.transfer(source, target, 50.0)
    assert result is True
    assert source.balance == 150.0
    assert target.balance == 200.0

    source2 = BankAccount("1234567892", "USD", "savings", 100.0)
    target2 = BankAccount("1234567893", "USD", "checking", 50.0)
    customer.add_account(source2)
    customer.add_account(target2)

    result2 = customer.transfer(source2, target2, 10.0)
    assert result2 is False
    assert source2.balance == 100.0
    assert target2.balance == 50.0
