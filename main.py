from __future__ import annotations

from datetime import date

from src.banking import BankAccount, Customer, InsufficientFundsError

customers: list[Customer] = []


def _find_customer(user_id: int) -> Customer | None:
    return next(
        (customer for customer in customers if customer._user_id == user_id), None
    )


def _read_customer() -> Customer | None:
    try:
        user_id = int(input("Customer user ID: "))
    except ValueError:
        print("User ID must be an integer.")
        return None

    customer = _find_customer(user_id)
    if customer is None:
        print("Customer not found.")
    return customer


def _add_customer() -> None:
    try:
        name = input("Customer name: ")
        birth_date = date.fromisoformat(input("Birth date (YYYY-MM-DD): "))
        customer = Customer(name, birth_date)
        customers.append(customer)
        print(f"Added customer {customer.name} with user ID {customer._user_id}.")
    except (TypeError, ValueError) as error:
        print(f"Could not add customer: {error}")


def _add_account() -> None:
    customer = _read_customer()
    if customer is None:
        return

    try:
        account_number = input("Account number (10 digits): ")
        currency = input("Currency [USD]: ") or "USD"
        account_type = input("Account type [checking/savings]: ") or "checking"
        initial_balance = float(input("Initial balance: "))
        if account_type == "savings":
            account = BankAccount.create_savings(
                account_number, currency, account_type, initial_balance
            )
        else:
            account = BankAccount(
                account_number, currency, account_type, initial_balance
            )
        customer.add_account(account)
        if customer.get_account(account_number) is None:
            print(
                "Account number must contain exactly 10 digits; account was not added."
            )
            return
        print(f"Added account {account_number} to customer {customer._user_id}.")
    except (TypeError, ValueError) as error:
        print(f"Could not add account: {error}")


def _read_account(customer: Customer, prompt: str) -> BankAccount | None:
    account_number = input(prompt)
    account = customer.get_account(account_number)
    if account is None:
        print("Account not found for this customer.")
    return account


def _perform_transaction() -> None:
    customer = _read_customer()
    if customer is None:
        return

    print("1. Deposit\n2. Withdraw\n3. Convert currency\n4. Transfer")
    transaction = input("Transaction: ")
    try:
        if transaction in {"1", "2", "3"}:
            account = _read_account(customer, "Account number: ")
            if account is None:
                return
            if transaction == "1":
                account.deposit(float(input("Amount: ")))
            elif transaction == "2":
                account.withdraw(float(input("Amount: ")))
            else:
                target_currency = input("Target currency: ")
                exchange_rate = float(input("Exchange rate: "))
                print(
                    f"Converted balance: {account.convert_currency(target_currency, exchange_rate):.2f}"
                )
            print(f"New balance: {account.balance:.2f} {account.currency}")
        elif transaction == "4":
            source = _read_account(customer, "Source account number: ")
            target = _read_account(customer, "Target account number: ")
            if source is None or target is None:
                return
            amount = float(input("Amount: "))
            if customer.transfer(source, target, amount):
                print("Transfer completed.")
            else:
                print("Transfer could not be completed.")
        else:
            print("Invalid transaction choice.")
    except (TypeError, ValueError, InsufficientFundsError) as error:
        print(f"Transaction failed: {error}")


def menu() -> None:
    while True:
        print("\n1. Add Customer\n2. Add BankAccount\n3. Perform transaction\n4. Exit")
        choice = input("Choose an option: ")
        if choice == "1":
            _add_customer()
        elif choice == "2":
            _add_account()
        elif choice == "3":
            _perform_transaction()
        elif choice == "4":
            print("Goodbye.")
            return
        else:
            print("Invalid option.")


def main() -> None:
    menu()


if __name__ == "__main__":
    menu()
