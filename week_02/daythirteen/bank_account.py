"""
Bank Account Class - Day 13 OOP Practice Project
A complete banking system implementation using Object-Oriented Programming
"""


class BankAccount:
    """
    A BankAccount class representing a simple bank account

    Attributes:
        account_holder (str): Name of the account holder
        account_number (str): Unique account identifier
        balance (float): Current account balance
        account_type (str): Type of account (Checking, Savings, etc.)
        transaction_history (list): Record of all transactions
    """

    # Class attributes
    bank_name = "Python National Bank"
    total_accounts_created = 0
    routing_number = "123456789"

    def __init__(self, account_holder, initial_balance=0, account_type="Checking"):
        """
        Initialize a new bank account

        Args:
            account_holder (str): Name of the account holder
            initial_balance (float): Starting balance (default 0)
            account_type (str): Type of account (default "Checking")
        """
        # Input validation
        if initial_balance < 0:
            raise ValueError("Initial balance cannot be negative")

        if not account_holder or not isinstance(account_holder, str):
            raise ValueError("Account holder name must be a non-empty string")

        # Instance attributes
        self.account_holder = account_holder
        self.balance = initial_balance
        self.account_type = account_type
        self.account_number = self._generate_account_number()
        self.transaction_history = []

        # Update class attribute
        BankAccount.total_accounts_created += 1

        # Record initial deposit if any
        if initial_balance > 0:
            self._record_transaction("Initial deposit", initial_balance)

        print(
            f"Created {account_type} account {self.account_number} for {account_holder}")

    def _generate_account_number(self):
        """Generate a unique account number"""
        return f"ACC{BankAccount.total_accounts_created + 1:08d}"

    def _record_transaction(self, description, amount):
        """
        Record a transaction in the history

        Args:
            description (str): Description of the transaction
            amount (float): Transaction amount (positive for deposits, negative for withdrawals)
        """
        transaction = {
            'description': description,
            'amount': amount,
            'balance_after': self.balance,
            'timestamp': self._get_current_timestamp()
        }
        self.transaction_history.append(transaction)

    def _get_current_timestamp(self):
        """Get current timestamp for transactions"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def deposit(self, amount):
        """
        Deposit money into the account

        Args:
            amount (float): Amount to deposit

        Returns:
            str: Confirmation message
        """
        if amount <= 0:
            return "Deposit amount must be positive"

        self.balance += amount
        self._record_transaction("Deposit", amount)

        return f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}"

    def withdraw(self, amount):
        """
        Withdraw money from the account

        Args:
            amount (float): Amount to withdraw

        Returns:
            str: Confirmation message or error
        """
        if amount <= 0:
            return "Withdrawal amount must be positive"

        if amount > self.balance:
            return "Insufficient funds for this withdrawal"

        self.balance -= amount
        self._record_transaction("Withdrawal", -amount)

        return f"Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}"

    def transfer(self, amount, target_account):
        """
        Transfer money to another BankAccount

        Args:
            amount (float): Amount to transfer
            target_account (BankAccount): Target account object

        Returns:
            str: Confirmation message or error
        """
        if not isinstance(target_account, BankAccount):
            return "Target must be a BankAccount object"

        if amount <= 0:
            return "Transfer amount must be positive"

        if amount > self.balance:
            return "Insufficient funds for this transfer"

        # Perform transfer
        self.balance -= amount
        target_account.balance += amount

        # Record transactions in both accounts
        self._record_transaction(
            f"Transfer to {target_account.account_number}", -amount)
        target_account._record_transaction(
            f"Transfer from {self.account_number}", amount)

        return (f"Transferred ${amount:.2f} to account {target_account.account_number}. "
                f"New balance: ${self.balance:.2f}")

    def get_balance(self):
        """
        Get current account balance

        Returns:
            str: Formatted balance information
        """
        return f"Current balance: ${self.balance:.2f}"

    def get_account_info(self):
        """
        Get complete account information

        Returns:
            str: Formatted account details
        """
        info = f"Bank: {BankAccount.bank_name}\n"
        info += f"Account Holder: {self.account_holder}\n"
        info += f"Account Number: {self.account_number}\n"
        info += f"Account Type: {self.account_type}\n"
        info += f"Current Balance: ${self.balance:.2f}\n"
        info += f"Total Transactions: {len(self.transaction_history)}"

        return info

    def get_transaction_history(self, last_n=None):
        """
        Get transaction history

        Args:
            last_n (int, optional): Number of recent transactions to return

        Returns:
            list: Transaction history
        """
        if last_n and last_n > 0:
            return self.transaction_history[-last_n:]
        return self.transaction_history

    def print_statement(self, last_n=10):
        """
        Print a formatted account statement

        Args:
            last_n (int): Number of recent transactions to include
        """
        print(f"\n{'=' * 50}")
        print(f"ACCOUNT STATEMENT - {BankAccount.bank_name}")
        print(f"{'=' * 50}")
        print(f"Account: {self.account_number}")
        print(f"Holder: {self.account_holder}")
        print(f"Type: {self.account_type}")
        print(f"Current Balance: ${self.balance:.2f}")
        print(f"{'=' * 50}")
        print("Recent Transactions:")
        print(f"{'=' * 50}")

        transactions = self.get_transaction_history(last_n)
        if not transactions:
            print("No transactions yet")
            return

        for transaction in transactions:
            amount_str = f"+${transaction['amount']:.2f}" if transaction[
                'amount'] > 0 else f"-${abs(transaction['amount']):.2f}"
            print(
                f"{transaction['timestamp']} | {transaction['description']:25} | {amount_str:>10} | Balance: ${transaction['balance_after']:.2f}")

    @classmethod
    def get_bank_info(cls):
        """
        Get bank-wide information

        Returns:
            str: Bank information
        """
        return (f"Bank: {cls.bank_name}\n"
                f"Routing Number: {cls.routing_number}\n"
                f"Total Accounts: {cls.total_accounts_created}")

    def __str__(self):
        """String representation of the account"""
        return f"BankAccount({self.account_holder}, ${self.balance:.2f})"

    def __repr__(self):
        """Technical representation of the account"""
        return f"BankAccount('{self.account_holder}', {self.balance}, '{self.account_type}')"


def demonstrate_bank_account():
    """Demonstrate the BankAccount class functionality"""
    print("BANK ACCOUNT CLASS DEMONSTRATION")
    print("=" * 60)

    # Display bank information
    print("Bank Information:")
    print(BankAccount.get_bank_info())
    print()

    # Create accounts
    print("Creating bank accounts:")
    account1 = BankAccount("Alice Johnson", 1000, "Checking")
    account2 = BankAccount("Bob Smith", 500, "Savings")
    account3 = BankAccount("Charlie Brown")  # Zero balance account

    print(f"\nTotal accounts created: {BankAccount.total_accounts_created}")

    # Test deposit functionality
    print("\n" + "=" * 40)
    print("DEPOSIT OPERATIONS")
    print("=" * 40)

    print(account1.deposit(250))
    print(account2.deposit(100))
    print(account3.deposit(50))
    print(account1.deposit(-100))  # Invalid deposit

    # Test withdrawal functionality
    print("\n" + "=" * 40)
    print("WITHDRAWAL OPERATIONS")
    print("=" * 40)

    print(account1.withdraw(200))
    print(account2.withdraw(50))
    print(account1.withdraw(2000))  # Should fail - insufficient funds
    print(account3.withdraw(-50))   # Invalid withdrawal

    # Test transfer functionality
    print("\n" + "=" * 40)
    print("TRANSFER OPERATIONS")
    print("=" * 40)

    print(account1.transfer(100, account3))
    print(account2.transfer(75, account1))
    # Should fail - insufficient funds
    print(account1.transfer(1000, account2))

    # Display account information
    print("\n" + "=" * 40)
    print("ACCOUNT INFORMATION")
    print("=" * 40)

    print("Account 1 Info:")
    print(account1.get_account_info())
    print()

    print("Account 2 Info:")
    print(account2.get_account_info())
    print()

    print("Account 3 Info:")
    print(account3.get_account_info())

    # Print statements
    print("\n" + "=" * 40)
    print("ACCOUNT STATEMENTS")
    print("=" * 40)

    account1.print_statement()
    print()
    account2.print_statement(5)  # Only last 5 transactions


def bank_account_interactive():
    """Interactive bank account demonstration"""
    print("\n" + "=" * 60)
    print("INTERACTIVE BANK ACCOUNT DEMONSTRATION")
    print("=" * 60)

    # Create a sample account
    account = BankAccount("Demo User", 1000)

    while True:
        print(f"\nCurrent Balance: ${account.balance:.2f}")
        print("\nOptions:")
        print("1. Deposit money")
        print("2. Withdraw money")
        print("3. View account info")
        print("4. Print statement")
        print("5. Exit")

        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == '1':
            try:
                amount = float(input("Enter deposit amount: $"))
                result = account.deposit(amount)
                print(result)
            except ValueError:
                print("Please enter a valid number")

        elif choice == '2':
            try:
                amount = float(input("Enter withdrawal amount: $"))
                result = account.withdraw(amount)
                print(result)
            except ValueError:
                print("Please enter a valid number")

        elif choice == '3':
            print("\nAccount Information:")
            print(account.get_account_info())

        elif choice == '4':
            account.print_statement()

        elif choice == '5':
            print("Thank you for using the bank system!")
            break

        else:
            print("Invalid choice. Please try again.")


if __name__ == "__main__":
    demonstrate_bank_account()
    bank_account_interactive()
