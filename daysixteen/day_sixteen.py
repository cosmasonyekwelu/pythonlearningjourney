"""
Python Learning Journey - Day Sixteen
Date: October 7 2025
Author: Cosmas Onyekwelu
Topic: Advanced OOP - Encapsulation and Properties: Protecting and Controlling Access to Data
"""


class EncapsulationFundamentals:
    """Demonstration of encapsulation concepts and property decorators"""

    def demonstrate_protected_attributes(self):
        """Protected attributes and access conventions"""
        print("=" * 60)
        print("Protected Attributes (_prefix)")
        print("=" * 60)

        class Employee:
            def __init__(self, name, salary, department):
                # Public attributes
                self.name = name
                self.department = department

                # Protected attributes (convention: internal use)
                self._salary = salary
                self._employee_id = self._generate_employee_id()
                self._performance_rating = 0

            def _generate_employee_id(self):
                """Protected method - for internal class use"""
                import random
                return f"EMP{random.randint(1000, 9999)}"

            def get_salary_info(self):
                """Public method that accesses protected attributes"""
                return f"Salary: ${self._salary:,.2f}"

            def _calculate_bonus(self):
                """Protected method for internal calculations"""
                return self._salary * (self._performance_rating / 100)

            def get_bonus(self):
                """Public interface to protected functionality"""
                bonus = self._calculate_bonus()
                return f"Bonus: ${bonus:,.2f}"

            def set_performance_rating(self, rating):
                """Controlled access to protected attribute"""
                if 0 <= rating <= 100:
                    self._performance_rating = rating
                    return f"Performance rating set to {rating}%"
                else:
                    return "Rating must be between 0 and 100"

        # Demonstrate protected attributes
        employee = Employee("Alice Johnson", 75000, "Engineering")

        print("Employee created:")
        print(f"Public attributes: {employee.name}, {employee.department}")
        print(f"Protected attributes accessed directly: {employee._salary}")
        print(f"Employee ID: {employee._employee_id}")

        print(f"\nUsing public methods to access protected data:")
        print(employee.get_salary_info())
        print(employee.set_performance_rating(85))
        print(employee.get_bonus())

        print(f"\nProtected attribute convention:")
        print("  _attribute_name - indicates 'internal use'")
        print("  Can still be accessed directly but shouldn't be")
        print("  Signals to other developers: use with care")

    def demonstrate_property_decorators(self):
        """Property decorators for controlled attribute access"""
        print("\n" + "=" * 60)
        print("Property Decorators (@property)")
        print("=" * 60)

        class Temperature:
            def __init__(self, celsius=0):
                # Store temperature in one base unit
                self._celsius = celsius

            @property
            def celsius(self):
                """Getter for celsius temperature"""
                return self._celsius

            @celsius.setter
            def celsius(self, value):
                """Setter for celsius with validation"""
                if value >= -273.15:  # Absolute zero
                    self._celsius = value
                else:
                    raise ValueError(
                        "Temperature cannot be below absolute zero (-273.15°C)")

            @property
            def fahrenheit(self):
                """Computed property - read-only"""
                return (self._celsius * 9/5) + 32

            @property
            def kelvin(self):
                """Another computed property - read-only"""
                return self._celsius + 273.15

            @property
            def description(self):
                """Computed property based on temperature"""
                if self._celsius < 0:
                    return "Freezing"
                elif self._celsius < 15:
                    return "Cold"
                elif self._celsius < 25:
                    return "Moderate"
                else:
                    return "Hot"

        # Demonstrate property usage
        temp = Temperature(20)

        print("Temperature properties:")
        print(f"Celsius: {temp.celsius}°C")  # Using property as attribute
        print(f"Fahrenheit: {temp.fahrenheit}°F")  # Computed property
        print(f"Kelvin: {temp.kelvin}K")  # Computed property
        print(f"Description: {temp.description}")

        # Using setter
        print(f"\nChanging temperature:")
        temp.celsius = 30  # Uses the setter
        print(f"New celsius: {temp.celsius}°C")
        print(f"New fahrenheit: {temp.fahrenheit}°F")
        print(f"New description: {temp.description}")

        # Error handling
        try:
            temp.celsius = -300  # This should raise ValueError
        except ValueError as e:
            print(f"Error setting temperature: {e}")

        print(f"\nProperty benefits:")
        print("  - Syntax looks like attribute access")
        print("  - Underlying implementation can have validation/logic")
        print("  - Computed properties behave like attributes")
        print("  - Backward compatible with existing code")

    def demonstrate_private_attributes(self):
        """Private attributes with name mangling"""
        print("\n" + "=" * 60)
        print("Private Attributes (__prefix) - Name Mangling")
        print("=" * 60)

        class SecureBankVault:
            def __init__(self, owner, initial_balance):
                self.owner = owner

                # Private attributes (name mangling)
                self.__balance = initial_balance
                self.__pin = "1234"  # Very secure ;)
                self.__transaction_history = []

                # Protected attribute
                self._vault_id = self.__generate_vault_id()

            def __generate_vault_id(self):
                """Private method - name mangled"""
                import hashlib
                return hashlib.md5(self.owner.encode()).hexdigest()[:8]

            def authenticate(self, pin_attempt):
                """Public method that uses private attributes"""
                if pin_attempt == self.__pin:
                    return True
                else:
                    self.__log_security_event("Failed authentication attempt")
                    return False

            def get_balance(self, pin):
                """Controlled access to private balance"""
                if self.authenticate(pin):
                    return f"Balance: ${self.__balance:,.2f}"
                return "Authentication failed"

            def deposit(self, amount, pin):
                """Controlled modification of private balance"""
                if self.authenticate(pin):
                    if amount > 0:
                        self.__balance += amount
                        self.__log_transaction(f"Deposit: ${amount:,.2f}")
                        return f"Deposited ${amount:,.2f}. New balance: ${self.__balance:,.2f}"
                    return "Deposit amount must be positive"
                return "Authentication failed"

            def __log_transaction(self, transaction):
                """Private method for internal logging"""
                self.__transaction_history.append(transaction)

            def __log_security_event(self, event):
                """Private method for security logging"""
                print(f"SECURITY: {event} for vault {self._vault_id}")

            def get_transaction_count(self, pin):
                """Public interface to private data"""
                if self.authenticate(pin):
                    return f"Total transactions: {len(self.__transaction_history)}"
                return "Authentication failed"

        # Demonstrate private attributes
        vault = SecureBankVault("John Doe", 5000)

        print("Secure Bank Vault created:")
        print(f"Public attribute: {vault.owner}")
        print(f"Protected attribute: {vault._vault_id}")

        # Try to access private attributes directly (will fail or show mangled names)
        print(f"\nTrying to access private attributes directly:")
        print(f"Direct access to __balance: (AttributeError expected)")
        try:
            print(vault.__balance)
        except AttributeError as e:
            print(f"  Error: {e}")

        # Don't do this!
        print(f"Actual mangled name: {vault._SecureBankVault__balance}")

        print(f"\nUsing proper public interface:")
        print(vault.get_balance("1234"))  # Correct PIN
        print(vault.get_balance("9999"))  # Wrong PIN
        print(vault.deposit(1000, "1234"))
        print(vault.get_transaction_count("1234"))

        print(f"\nName mangling explanation:")
        print("  __attribute_name becomes _ClassName__attribute_name")
        print("  Provides name spacing to avoid subclass conflicts")
        print("  Not truly private, but strongly discouraged from external access")

    def demonstrate_comprehensive_validation(self):
        """Comprehensive data validation using properties"""
        print("\n" + "=" * 60)
        print("Comprehensive Validation with Properties")
        print("=" * 60)

        class Student:
            def __init__(self, name, age, email):
                self._name = name
                self._age = age
                self._email = email
                self._grades = []
                self._gpa = 0.0

            @property
            def name(self):
                return self._name

            @name.setter
            def name(self, value):
                if not value or not isinstance(value, str):
                    raise ValueError("Name must be a non-empty string")
                if len(value) < 2:
                    raise ValueError("Name must be at least 2 characters long")
                self._name = value

            @property
            def age(self):
                return self._age

            @age.setter
            def age(self, value):
                if not isinstance(value, int):
                    raise ValueError("Age must be an integer")
                if value < 5 or value > 120:
                    raise ValueError("Age must be between 5 and 120")
                self._age = value

            @property
            def email(self):
                return self._email

            @email.setter
            def email(self, value):
                import re
                pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(pattern, value):
                    raise ValueError("Invalid email format")
                self._email = value

            @property
            def grades(self):
                return self._grades.copy()  # Return copy to prevent external modification

            def add_grade(self, grade):
                if not isinstance(grade, (int, float)):
                    raise ValueError("Grade must be a number")
                if grade < 0 or grade > 100:
                    raise ValueError("Grade must be between 0 and 100")
                self._grades.append(grade)
                self._update_gpa()

            @property
            def gpa(self):
                """Read-only computed property"""
                return self._gpa

            def _update_gpa(self):
                """Private method to update GPA"""
                if self._grades:
                    # Simple GPA calculation (scale 0-4)
                    total = sum(self._grades)
                    average = total / len(self._grades)
                    # Convert 0-100 to 0-4 scale
                    self._gpa = min(4.0, average / 25)

            @property
            def academic_standing(self):
                """Computed property based on GPA"""
                if self._gpa >= 3.5:
                    return "Excellent"
                elif self._gpa >= 3.0:
                    return "Good"
                elif self._gpa >= 2.0:
                    return "Satisfactory"
                else:
                    return "Needs Improvement"

            def get_student_info(self):
                return (f"Student: {self.name}, Age: {self.age}\n"
                        f"Email: {self.email}, GPA: {self.gpa:.2f}\n"
                        f"Academic Standing: {self.academic_standing}\n"
                        f"Grades: {self.grades}")

        # Demonstrate comprehensive validation
        student = Student("Alice Smith", 20, "alice@university.edu")

        print("Student created with validation:")
        print(student.get_student_info())

        print(f"\nAdding grades:")
        student.add_grade(85)
        student.add_grade(92)
        student.add_grade(78)
        print(student.get_student_info())

        print(f"\nProperty validation in action:")
        try:
            student.age = 150  # Invalid age
        except ValueError as e:
            print(f"Age validation error: {e}")

        try:
            student.email = "invalid-email"  # Invalid email
        except ValueError as e:
            print(f"Email validation error: {e}")

        try:
            student.add_grade(150)  # Invalid grade
        except ValueError as e:
            print(f"Grade validation error: {e}")

        # Valid changes
        student.name = "Alice Johnson"
        student.age = 21
        student.email = "alice.johnson@university.edu"
        print(f"\nAfter valid updates:")
        print(student.get_student_info())


class BankAccountProject:
    """Practice Project: Enhanced Bank Account class with property-based validation"""

    def create_enhanced_bank_account(self):
        """Comprehensive Bank Account with encapsulation and properties"""
        print("\n" + "=" * 60)
        print("Enhanced Bank Account Project")
        print("=" * 60)

        class BankAccount:
            def __init__(self, account_holder, initial_balance=0, account_type="Checking"):
                # Public attributes
                self.account_holder = account_holder
                self.account_type = account_type

                # Protected attributes
                self._account_number = self._generate_account_number()
                self._opening_date = self._get_current_date()

                # Private attributes
                self.__balance = 0
                self.__transaction_history = []
                self.__is_active = True
                self.__overdraft_limit = 100  # Private overdraft protection

                # Use setter for initial balance to trigger validation
                self.balance = initial_balance

                # Log account creation
                self.__log_transaction("Account opened", initial_balance)

            def _generate_account_number(self):
                """Protected method for account number generation"""
                import random
                return f"ACC{random.randint(100000, 999999)}"

            def _get_current_date(self):
                """Protected method for date handling"""
                from datetime import datetime
                return datetime.now().strftime("%Y-%m-%d")

            # Balance property with comprehensive validation
            @property
            def balance(self):
                """Getter for balance - read access"""
                return self.__balance

            @balance.setter
            def balance(self, value):
                """Setter for balance with validation"""
                if not isinstance(value, (int, float)):
                    raise ValueError("Balance must be a number")

                if value < -self.__overdraft_limit:
                    raise ValueError(
                        f"Insufficient funds. Overdraft limit is ${self.__overdraft_limit}")

                self.__balance = round(value, 2)

            # Read-only properties
            @property
            def account_number(self):
                """Read-only property for account number"""
                return self._account_number

            @property
            def opening_date(self):
                """Read-only property for opening date"""
                return self._opening_date

            @property
            def is_active(self):
                """Read-only property for account status"""
                return self.__is_active

            @property
            def transaction_count(self):
                """Computed property for transaction count"""
                return len(self.__transaction_history)

            @property
            def available_balance(self):
                """Computed property including overdraft"""
                return self.__balance + self.__overdraft_limit

            # Account operations with encapsulation
            def deposit(self, amount):
                """Deposit money with validation"""
                if not self.__is_active:
                    raise ValueError("Cannot deposit to inactive account")

                if amount <= 0:
                    raise ValueError("Deposit amount must be positive")

                old_balance = self.__balance
                self.balance = self.__balance + amount  # Use property setter
                self.__log_transaction("Deposit", amount)

                return f"Deposited ${amount:.2f}. Balance: ${self.__balance:.2f}"

            def withdraw(self, amount):
                """Withdraw money with validation"""
                if not self.__is_active:
                    raise ValueError("Cannot withdraw from inactive account")

                if amount <= 0:
                    raise ValueError("Withdrawal amount must be positive")

                if amount > self.available_balance:
                    raise ValueError(
                        f"Insufficient funds. Available: ${self.available_balance:.2f}")

                old_balance = self.__balance
                self.balance = self.__balance - amount  # Use property setter
                self.__log_transaction("Withdrawal", -amount)

                return f"Withdrew ${amount:.2f}. Balance: ${self.__balance:.2f}"

            def transfer(self, amount, target_account):
                """Transfer money to another account"""
                if not isinstance(target_account, BankAccount):
                    raise ValueError("Target must be a BankAccount")

                # First withdraw from this account
                self.withdraw(amount)

                # Then deposit to target account
                target_account.deposit(amount)

                self.__log_transaction(
                    f"Transfer to {target_account.account_number}", -amount)
                target_account.__log_transaction(
                    f"Transfer from {self.account_number}", amount)

                return f"Transferred ${amount:.2f} to {target_account.account_holder}"

            def apply_interest(self, rate):
                """Apply interest to account balance"""
                if not self.__is_active:
                    raise ValueError(
                        "Cannot apply interest to inactive account")

                if rate <= 0:
                    raise ValueError("Interest rate must be positive")

                interest = self.__balance * (rate / 100)
                self.balance = self.__balance + interest
                self.__log_transaction("Interest", interest)

                return f"Applied ${interest:.2f} interest at {rate}%"

            # Account management
            def close_account(self):
                """Close the bank account"""
                if self.__balance != 0:
                    raise ValueError(
                        "Cannot close account with non-zero balance")

                self.__is_active = False
                self.__log_transaction("Account closed", 0)
                return "Account closed successfully"

            def get_account_statement(self, last_n=5):
                """Get account statement with recent transactions"""
                statement = [
                    f"Account Statement - {self._account_number}",
                    f"Holder: {self.account_holder}",
                    f"Type: {self.account_type}",
                    f"Status: {'Active' if self.__is_active else 'Closed'}",
                    f"Current Balance: ${self.__balance:.2f}",
                    f"Available Balance: ${self.available_balance:.2f}",
                    f"Opening Date: {self._opening_date}",
                    "",
                    f"Last {last_n} Transactions:"
                ]

                recent_transactions = self.__transaction_history[-last_n:]
                for transaction in recent_transactions:
                    amount_str = f"+${transaction['amount']:.2f}" if transaction[
                        'amount'] > 0 else f"-${abs(transaction['amount']):.2f}"
                    statement.append(
                        f"  {transaction['date']} | {transaction['description']:20} | {amount_str:>10} | Balance: ${transaction['balance_after']:.2f}")

                return "\n".join(statement)

            # Private methods for internal use
            def __log_transaction(self, description, amount):
                """Private method to log transactions"""
                from datetime import datetime

                transaction = {
                    'date': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'description': description,
                    'amount': amount,
                    'balance_after': self.__balance
                }
                self.__transaction_history.append(transaction)

            def __validate_transaction_amount(self, amount):
                """Private validation method"""
                if not isinstance(amount, (int, float)):
                    raise ValueError("Amount must be a number")
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                return True

            # String representations
            def __str__(self):
                return f"BankAccount({self.account_holder}, ${self.__balance:.2f})"

            def __repr__(self):
                return f"BankAccount('{self.account_holder}', {self.__balance}, '{self.account_type}')"

        # Demonstrate the enhanced Bank Account
        print("Creating bank accounts with encapsulation:")

        # Create accounts
        account1 = BankAccount("Alice Johnson", 1000, "Checking")
        account2 = BankAccount("Bob Smith", 500, "Savings")

        print(
            f"Account 1: {account1.account_holder} - {account1.account_number}")
        print(
            f"Account 2: {account2.account_holder} - {account2.account_number}")

        # Demonstrate operations
        print("\n" + "-" * 40)
        print("Banking Operations")
        print("-" * 40)

        print(account1.deposit(250))
        print(account1.withdraw(200))
        print(account2.deposit(100))

        print(f"\nTransfer demonstration:")
        print(account1.transfer(150, account2))

        print(f"\nInterest application:")
        print(account2.apply_interest(2.5))  # 2.5% interest

        # Demonstrate property access
        print("\n" + "-" * 40)
        print("Property Access Demonstration")
        print("-" * 40)

        print(f"Account 1 balance: ${account1.balance:.2f}")
        print(f"Account 1 available: ${account1.available_balance:.2f}")
        print(f"Account 1 transactions: {account1.transaction_count}")
        print(f"Account 1 active: {account1.is_active}")

        # Demonstrate validation
        print("\n" + "-" * 40)
        print("Validation Demonstration")
        print("-" * 40)

        try:
            account1.balance = -200  # This should fail
        except ValueError as e:
            print(f"Balance validation: {e}")

        try:
            account1.withdraw(2000)  # This should fail
        except ValueError as e:
            print(f"Withdrawal validation: {e}")

        try:
            account1.deposit(-100)  # This should fail
        except ValueError as e:
            print(f"Deposit validation: {e}")

        # Account statements
        print("\n" + "-" * 40)
        print("Account Statements")
        print("-" * 40)

        print("Account 1 Statement:")
        print(account1.get_account_statement())

        print(f"\nAccount 2 Statement:")
        print(account2.get_account_statement(3))

        # Demonstrate encapsulation benefits
        print("\n" + "-" * 40)
        print("Encapsulation Benefits")
        print("-" * 40)

        print("Protected and private attributes:")
        # Accessible but internal
        print(f"  Protected (_account_number): {account1._account_number}")
        try:
            # Should fail
            print(f"  Private (__balance): {account1.__balance}")
        except AttributeError:
            print("  Private (__balance): Not directly accessible (name mangled)")

        print(f"  Through property: ${account1.balance:.2f}")


class PracticeExercises:
    """Additional practice exercises for encapsulation"""

    def create_temperature_converter(self):
        """Temperature converter with property validation"""
        print("\n" + "=" * 50)
        print("Temperature Converter Exercise")
        print("=" * 50)

        class TemperatureConverter:
            def __init__(self, celsius=0):
                self._celsius = celsius

            @property
            def celsius(self):
                return self._celsius

            @celsius.setter
            def celsius(self, value):
                if value < -273.15:
                    raise ValueError(
                        "Temperature cannot be below absolute zero")
                self._celsius = value

            @property
            def fahrenheit(self):
                return (self._celsius * 9/5) + 32

            @fahrenheit.setter
            def fahrenheit(self, value):
                self.celsius = (value - 32) * 5/9

            @property
            def kelvin(self):
                return self._celsius + 273.15

            @kelvin.setter
            def kelvin(self, value):
                if value < 0:
                    raise ValueError("Kelvin cannot be negative")
                self.celsius = value - 273.15

            @property
            def description(self):
                if self._celsius < 0:
                    return "Freezing"
                elif self._celsius < 10:
                    return "Cold"
                elif self._celsius < 20:
                    return "Cool"
                elif self._celsius < 30:
                    return "Warm"
                else:
                    return "Hot"

        # Demonstrate temperature converter
        temp = TemperatureConverter(25)

        print("Temperature conversions:")
        print(f"Celsius: {temp.celsius}°C")
        print(f"Fahrenheit: {temp.fahrenheit}°F")
        print(f"Kelvin: {temp.kelvin}K")
        print(f"Description: {temp.description}")

        print(f"\nSetting via different scales:")
        temp.fahrenheit = 100
        print(f"100°F = {temp.celsius}°C")

        temp.kelvin = 300
        print(f"300K = {temp.celsius}°C")

        # Validation test
        try:
            temp.celsius = -300
        except ValueError as e:
            print(f"Validation: {e}")


def main():
    """Main execution function"""
    print("DAY 16: ADVANCED OOP - ENCAPSULATION AND PROPERTIES")
    print("=" * 70)

    # Initialize classes
    encapsulation_demo = EncapsulationFundamentals()
    bank_project = BankAccountProject()
    practice_exercises = PracticeExercises()

    # Demonstrate encapsulation concepts
    encapsulation_demo.demonstrate_protected_attributes()
    encapsulation_demo.demonstrate_property_decorators()
    encapsulation_demo.demonstrate_private_attributes()
    encapsulation_demo.demonstrate_comprehensive_validation()

    # Bank Account project
    print("\n" + "=" * 70)
    print("PRACTICE PROJECT: ENHANCED BANKACCOUNT")
    print("=" * 70)

    bank_project.create_enhanced_bank_account()

    # Additional practice exercises
    print("\n" + "=" * 70)
    print("ADDITIONAL PRACTICE EXERCISES")
    print("=" * 70)

    practice_exercises.create_temperature_converter()

    print("\n" + "=" * 70)
    print("DAY 16 COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("Key concepts mastered:")
    print("- Protected attributes (_prefix) for internal use")
    print("- Property decorators (@property) for controlled access")
    print("- Private attributes (__prefix) with name mangling")
    print("- Data validation through setter methods")
    print("- Read-only and computed properties")
    print("- Comprehensive encapsulation in real-world classes")


if __name__ == "__main__":
    main()
