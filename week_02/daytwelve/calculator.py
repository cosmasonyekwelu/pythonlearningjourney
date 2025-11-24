"""
Safe Calculator Module
Day 12 Mini-Project: A robust calculator with comprehensive error handling
"""


class CalculatorError(Exception):
    """Base exception for calculator operations"""
    pass


class DivisionByZeroError(CalculatorError):
    """Exception raised for division by zero"""
    pass


class InvalidInputError(CalculatorError):
    """Exception raised for invalid user input"""
    pass


class InvalidOperatorError(CalculatorError):
    """Exception raised for invalid operators"""
    pass


class SafeCalculator:
    """A robust calculator with comprehensive error handling"""

    def __init__(self):
        self.operations = {
            '+': self._add,
            '-': self._subtract,
            '*': self._multiply,
            '/': self._divide,
            '**': self._power,
            '//': self._floor_divide,
            '%': self._modulo
        }
        self.history = []

    def _add(self, a, b):
        return a + b

    def _subtract(self, a, b):
        return a - b

    def _multiply(self, a, b):
        return a * b

    def _divide(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Cannot divide by zero")
        return a / b

    def _power(self, a, b):
        try:
            return a ** b
        except OverflowError:
            raise CalculatorError("Result too large")

    def _floor_divide(self, a, b):
        if b == 0:
            raise DivisionByZeroError(
                "Cannot perform integer division by zero")
        return a // b

    def _modulo(self, a, b):
        if b == 0:
            raise DivisionByZeroError("Cannot perform modulo by zero")
        return a % b

    def validate_number(self, value):
        """Validate and convert input to number"""
        try:
            return float(value)
        except (ValueError, TypeError):
            raise InvalidInputError(f"'{value}' is not a valid number")

    def validate_operator(self, operator):
        """Validate operator"""
        if operator not in self.operations:
            raise InvalidOperatorError(f"Unknown operator: '{operator}'")
        return operator

    def calculate(self, num1, num2, operator):
        """Perform calculation with comprehensive error handling"""
        try:
            # Validate inputs
            validated_num1 = self.validate_number(num1)
            validated_num2 = self.validate_number(num2)
            validated_operator = self.validate_operator(operator)

            # Perform calculation
            operation_func = self.operations[validated_operator]
            result = operation_func(validated_num1, validated_num2)

            # Record in history
            calculation_record = {
                'num1': validated_num1,
                'num2': validated_num2,
                'operator': validated_operator,
                'result': result
            }
            self.history.append(calculation_record)

            return result

        except CalculatorError:
            # Re-raise known calculator errors
            raise
        except Exception as e:
            # Handle unexpected errors
            raise CalculatorError(f"Unexpected error during calculation: {e}")

    def get_history(self):
        """Get calculation history"""
        return self.history.copy()

    def clear_history(self):
        """Clear calculation history"""
        self.history.clear()

    def display_history(self):
        """Display calculation history in readable format"""
        if not self.history:
            print("No calculations in history")
            return

        print("\nCalculation History:")
        for i, record in enumerate(self.history, 1):
            print(
                f"{i}. {record['num1']} {record['operator']} {record['num2']} = {record['result']}")


def run_calculator():
    """Run the interactive calculator interface"""
    calculator = SafeCalculator()

    print("=" * 50)
    print("SAFE CALCULATOR")
    print("=" * 50)
    print("Available operations: +, -, *, /, **, //, %")
    print("Enter 'history' to view calculation history")
    print("Enter 'clear' to clear history")
    print("Enter 'quit' to exit")
    print("-" * 50)

    while True:
        try:
            user_input = input(
                "\nEnter calculation (e.g., 5 + 3) or command: ").strip()

            if user_input.lower() == 'quit':
                print("Thank you for using Safe Calculator!")
                break
            elif user_input.lower() == 'history':
                calculator.display_history()
                continue
            elif user_input.lower() == 'clear':
                calculator.clear_history()
                print("History cleared")
                continue
            elif not user_input:
                continue

            # Parse input
            parts = user_input.split()
            if len(parts) != 3:
                print("Error: Please use format 'number operator number'")
                continue

            num1_str, operator, num2_str = parts

            # Perform calculation
            result = calculator.calculate(num1_str, num2_str, operator)
            print(f"Result: {num1_str} {operator} {num2_str} = {result}")

        except CalculatorError as e:
            print(f"Calculator Error: {e}")
        except KeyboardInterrupt:
            print("\nCalculator stopped by user")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")


if __name__ == "__main__":
    run_calculator()
