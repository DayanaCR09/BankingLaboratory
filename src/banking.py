"""Banking application logic."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime

logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


class InsufficientFundsError(Exception):
    """Raised when a withdrawal amount exceeds the available balance."""

    def __init__(self, message: str, attempted_amount: float) -> None:
        super().__init__(message)
        self.message = message
        self.attempted_amount = attempted_amount


class BankAccount:
    """Simple bank account with deposit and withdrawal support."""

    def __init__(
        self,
        account_number: str,
        currency: str = "USD",
        account_type: str = "checking",
        initial_balance: float = 0.0,
    ) -> None:
        self.account_number = account_number
        self.currency = currency
        self._account_type = account_type
        self.__balance = 0.0
        self.balance = initial_balance
        logger.info(
            "Account created for %s (%s) with balance %s.",
            self.account_number,
            self._account_type,
            self.format_currency(self.__balance, self.currency),
        )

    def get_account_number(self) -> str:
        return self.account_number

    def get_currency(self) -> str:
        return self.currency

    def get_account_type(self) -> str:
        return self._account_type

    def get_balance(self) -> float:
        return self.__balance

    def set_balance(self, value: float) -> None:
        if value < 0:
            logger.error("Balance update failed: balance cannot be negative.")
            raise ValueError("Balance cannot be negative.")
        self.__balance = float(value)

    @property
    def balance(self) -> float:
        return self.__balance

    @balance.setter
    def balance(self, value: float) -> None:
        self.set_balance(value)

    @staticmethod
    def is_valid_account_number(account_number: str) -> bool:
        return (
            bool(account_number)
            and account_number.isdigit()
            and len(account_number) == 10
        )

    @staticmethod
    def format_currency(amount: float, currency: str = "USD") -> str:
        return f"{amount:.2f} {currency}"

    @classmethod
    def from_snapshot(
        cls,
        account_number: str,
        currency: str = "USD",
        account_type: str = "checking",
        initial_balance: float = 0.0,
    ) -> BankAccount:
        return cls(account_number, currency, account_type, initial_balance)

    @classmethod
    def create_savings(
        cls,
        account_number: str,
        currency: str = "USD",
        account_type: str = "savings",
        initial_balance: float = 100.0,
    ) -> BankAccount:
        minimum_balance = 100.0
        if initial_balance < minimum_balance:
            logger.error(
                "Savings account creation failed: initial balance cannot be below %s.",
                cls.format_currency(minimum_balance, currency),
            )
            raise ValueError("Savings account initial balance cannot be below $100.00.")
        return cls(account_number, currency, account_type, initial_balance)

    def deposit(self, amount: float) -> float:
        if amount < 0:
            logger.error("Deposit failed: amount cannot be negative.")
            raise ValueError("Deposit amount cannot be negative.")
        if amount == 0:
            logger.error("Deposit failed: deposit amount must be positive.")
            raise ValueError("Deposit amount must be positive.")
        self.__balance += amount
        logger.info(
            "Deposited %s for account %s. New balance: %s.",
            self.format_currency(amount, self.currency),
            self.account_number,
            self.format_currency(self.__balance, self.currency),
        )
        return self.__balance

    def withdraw(self, amount: float) -> float:
        if amount < 0:
            logger.error("Withdrawal failed: amount cannot be negative.")
            raise ValueError("Withdrawal amount cannot be negative.")
        if amount == 0:
            logger.error("Withdrawal failed: withdrawal amount must be positive.")
            raise ValueError("Withdrawal amount must be positive.")

        minimum_balance = 100.0 if self._account_type == "savings" else 0.0
        projected_balance = self.__balance - amount

        if projected_balance < minimum_balance:
            message = (
                f"Insufficient funds for account {self.account_number}. "
                f"Requested {self.format_currency(amount, self.currency)}, "
                f"available {self.format_currency(self.__balance, self.currency)}. "
                f"Minimum required balance is {self.format_currency(minimum_balance, self.currency)}."
            )
            logger.error(message)
            raise InsufficientFundsError(message, amount)

        self.__balance = projected_balance
        logger.info(
            "Withdrew %s from account %s. New balance: %s.",
            self.format_currency(amount, self.currency),
            self.account_number,
            self.format_currency(self.__balance, self.currency),
        )
        return self.__balance

    def convert_currency(self, target_currency: str, exchange_rate: float) -> float:
        if exchange_rate <= 0:
            logger.error("Currency conversion failed: exchange rate must be positive.")
            raise ValueError("Exchange rate must be positive.")

        converted_balance = self.__balance * exchange_rate
        logger.info(
            "Converted %s from %s to %s at rate %.2f. Result: %s %s.",
            self.format_currency(self.__balance, self.currency),
            self.currency,
            target_currency,
            exchange_rate,
            converted_balance,
            target_currency,
        )
        return converted_balance

    def __str__(self) -> str:
        return f"{self.account_number}: {self.format_currency(self.__balance, self.currency)}"


class Customer:
    """A customer who may hold multiple bank accounts."""

    user_count = 0

    def __init__(self, name: str, birth_date: date) -> None:
        self._name = ""
        self._birth_date = None
        self.__accounts: list[BankAccount] = []
        Customer.user_count += 1
        self._user_id = Customer.user_count

        self.name = name
        self.birth_date = birth_date

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        if not value or not value.strip():
            raise ValueError("Customer name cannot be empty.")
        self._name = value.strip()

    @property
    def birth_date(self) -> date:
        return self._birth_date

    @birth_date.setter
    def birth_date(self, value: date) -> None:
        if not isinstance(value, date):
            raise TypeError("Birth date must be a date object.")
        today = datetime.now(UTC).date()
        age = (
            today.year
            - value.year
            - ((today.month, today.day) < (value.month, value.day))
        )
        if age < 18:
            raise ValueError("Customer must be at least 18 years old.")
        self._birth_date = value

    @property
    def user_id(self) -> int:
        return self._user_id

    @property
    def accounts(self) -> list[BankAccount]:
        return list(self.__accounts)

    @staticmethod
    def is_valid_customer_id(customer_id: str) -> bool:
        return bool(customer_id) and customer_id.strip() != ""

    @classmethod
    def from_snapshot(
        cls, name: str, birth_date: date, accounts: list[BankAccount] | None = None
    ) -> Customer:
        customer = cls(name, birth_date)
        if accounts:
            customer.__accounts = list(accounts)
        return customer

    def add_account(self, account: BankAccount) -> None:
        if not isinstance(account, BankAccount):
            raise TypeError("Only BankAccount instances can be added.")
        if not BankAccount.is_valid_account_number(account.account_number):
            logger.error(
                "Account %s is invalid and could not be added.", account.account_number
            )
            return
        self.__accounts.append(account)

    def get_account(self, account_number: str) -> BankAccount | None:
        for account in self.__accounts:
            if account.account_number == account_number:
                return account
        return None

    def total_balance(self) -> float:
        return sum(account.balance for account in self.__accounts)

    def get_total_balance(self) -> float:
        total = 0.0
        for account in self.__accounts:
            total += account.balance
        return total

    def transfer(
        self, source_account: BankAccount, target_account: BankAccount, amount: float
    ) -> bool:
        if not isinstance(source_account, BankAccount) or not isinstance(
            target_account, BankAccount
        ):
            logger.error(
                "Transfer failed: source and target must be valid BankAccount instances."
            )
            return False

        if amount <= 0:
            logger.error("Transfer failed: transfer amount must be positive.")
            return False

        source_in_customer = source_account in self.__accounts
        target_in_customer = target_account in self.__accounts
        if not source_in_customer or not target_in_customer:
            logger.error("Transfer failed: both accounts must belong to this customer.")
            return False

        source_min = 100.0 if source_account._account_type == "savings" else 0.0
        target_min = 100.0 if target_account._account_type == "savings" else 0.0

        if source_account.balance - amount < source_min:
            logger.error(
                "Transfer failed: source account %s would violate the minimum balance requirement.",
                source_account.account_number,
            )
            return False

        if (
            target_account._account_type == "savings"
            and target_account.balance + amount < target_min
        ):
            logger.error(
                "Transfer failed: target savings account %s would violate the minimum balance requirement.",
                target_account.account_number,
            )
            return False

        source_account.withdraw(amount)
        target_account.deposit(amount)
        logger.info(
            "Transferred %s from account %s to account %s.",
            BankAccount.format_currency(amount, source_account.currency),
            source_account.account_number,
            target_account.account_number,
        )
        return True

    def __str__(self) -> str:
        return f"User {self._user_id}: {self._name} ({len(self.__accounts)} accounts)"
