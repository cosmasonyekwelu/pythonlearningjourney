import logging
import pdb
from datetime import datetime
import sys
import traceback


class ValidationError(Exception):
    """Custom exception for input validation errors"""

    def __init__(self, message, value=None):
        self.message = message
        self.value = value
        super().__init__(self.message)


class CalculationError(Exception):
    """Custom exception for calculation errors"""
    pass


class ErrorLogger:
    def __init__(self, log_file='error_log.txt'):
        self.log_file = log_file
        self.setup_logging()

    def setup_logging(self):
        """Configure logging settings"""
        logging.basicConfig(
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger()

    def log_error(self, error_type, error_message, user_input=None):
        """Log errors with contextual information"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'error_type': error_type,
            'message': error_message,
            'user_input': user_input
        }

        self.logger.error(
            f"{error_type}: {error_message} | Input: {user_input}")
        return log_entry


class InputValidator:
    def __init__(self, error_logger):
        self.error_logger = error_logger

    def validate_integer(self, input_str):
        """Validate and convert string to integer with comprehensive error handling"""
        try:
            if not input_str.strip():
                raise ValidationError("Input cannot be empty", input_str)

            value = int(input_str)

            if value < 0:
                raise ValidationError("Input must be positive", value)

            return value

        except ValueError as e:
            self.error_logger.log_error(
                "ValueError",
                f"Invalid integer input: {input_str}",
                input_str
            )
            raise ValidationError(
                f"'{input_str}' is not a valid integer", input_str) from e

        except ValidationError as e:
            self.error_logger.log_error(
                "ValidationError",
                e.message,
                input_str
            )
            raise

    def validate_float(self, input_str):
        """Validate and convert string to float"""
        try:
            if not input_str.strip():
                raise ValidationError("Input cannot be empty", input_str)

            value = float(input_str)
            return value

        except ValueError as e:
            self.error_logger.log_error(
                "ValueError",
                f"Invalid float input: {input_str}",
                input_str
            )
            raise ValidationError(
                f"'{input_str}' is not a valid number", input_str) from e

    def validate_string(self, input_str, min_length=1, max_length=100):
        """Validate string input"""
        try:
            if not isinstance(input_str, str):
                raise ValidationError("Input must be a string", input_str)

            cleaned_input = input_str.strip()

            if len(cleaned_input) < min_length:
                raise ValidationError(
                    f"Input must be at least {min_length} characters long",
                    input_str
                )

            if len(cleaned_input) > max_length:
                raise ValidationError(
                    f"Input cannot exceed {max_length} characters",
                    input_str
                )

            return cleaned_input

        except ValidationError as e:
            self.error_logger.log_error(
                "ValidationError",
                e.message,
                input_str
            )
            raise


class Calculator:
    def __init__(self, error_logger):
        self.error_logger = error_logger
        self.validator = InputValidator(error_logger)

    def safe_divide(self, numerator_str, denominator_str):
        """Perform division with comprehensive error handling"""
        try:
            # Debugging point - uncomment to use pdb
            # pdb.set_trace()

            numerator = self.validator.validate_float(numerator_str)
            denominator = self.validator.validate_float(denominator_str)

            if denominator == 0:
                raise CalculationError("Division by zero is not allowed")

            result = numerator / denominator

            self.error_logger.logger.info(
                f"Division operation: {numerator} / {denominator} = {result}"
            )

            return result

        except CalculationError as e:
            self.error_logger.log_error(
                "CalculationError",
                str(e),
                f"{numerator_str}/{denominator_str}"
            )
            raise

        except ValidationError as e:
            # Already logged in validator
            raise CalculationError(f"Invalid input: {e.message}") from e

        except Exception as e:
            self.error_logger.log_error(
                "UnexpectedError",
                f"Unexpected error in division: {str(e)}",
                f"{numerator_str}/{denominator_str}"
            )
            raise CalculationError("An unexpected error occurred") from e

    def calculate_power(self, base_str, exponent_str):
        """Calculate power with error handling"""
        try:
            base = self.validator.validate_float(base_str)
            exponent = self.validator.validate_float(exponent_str)

            if base == 0 and exponent < 0:
                raise CalculationError(
                    "Zero cannot be raised to a negative power")

            result = base ** exponent

            self.error_logger.logger.info(
                f"Power operation: {base} ** {exponent} = {result}"
            )

            return result

        except OverflowError as e:
            self.error_logger.log_error(
                "OverflowError",
                "Result too large for calculation",
                f"{base_str}**{exponent_str}"
            )
            raise CalculationError("Result is too large") from e

        except Exception as e:
            self.error_logger.log_error(
                "CalculationError",
                str(e),
                f"{base_str}**{exponent_str}"
            )
            raise


def demonstrate_exception_hierarchy():
    """Demonstrate Python's exception hierarchy"""
    print("\n" + "="*50)
    print("EXCEPTION HIERARCHY DEMONSTRATION")
    print("="*50)

    exceptions_demo = [
        (ValueError, "Invalid value"),
        (TypeError, "Incorrect type"),
        (ZeroDivisionError, "Division by zero"),
        (IndexError, "List index out of range"),
        (KeyError, "Dictionary key not found"),
        (FileNotFoundError, "File does not exist"),
    ]

    for exc_type, description in exceptions_demo:
        try:
            if exc_type == ValueError:
                raise ValueError(description)
            elif exc_type == TypeError:
                raise TypeError(description)
            elif exc_type == ZeroDivisionError:
                raise ZeroDivisionError(description)
            elif exc_type == IndexError:
                raise IndexError(description)
            elif exc_type == KeyError:
                raise KeyError(description)
            elif exc_type == FileNotFoundError:
                raise FileNotFoundError(description)

        except Exception as e:
            print(f"Caught {type(e).__name__}: {e}")
            print(f"  Is it an Exception? {isinstance(e, Exception)}")
            print(f"  Is it a BaseException? {isinstance(e, BaseException)}")


def interactive_debugging_demo():
    """Demonstrate interactive debugging techniques"""
    print("\n" + "="*50)
    print("DEBUGGING DEMONSTRATION")
    print("="*50)

    def buggy_function(numbers):
        # This function has a bug - let's find it!
        total = 0
        for i in range(len(numbers) + 1):  # Intentional bug: off-by-one error
            total += numbers[i]
        return total

    try:
        result = buggy_function([1, 2, 3, 4, 5])
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error occurred: {e}")
        print("\nUsing traceback to debug:")
        traceback.print_exc()

        print("\nDebugging tips:")
        print("1. Use pdb.set_trace() to set breakpoints")
        print("2. Use logging to track variable values")
        print("3. Use try-except to catch and analyze errors")


def view_error_log():
    """Display the contents of the error log"""
    try:
        with open('error_log.txt', 'r') as f:
            content = f.read()
            if content:
                print("\n" + "="*50)
                print("ERROR LOG CONTENTS")
                print("="*50)
                print(content)
            else:
                print("Error log is empty")
    except FileNotFoundError:
        print("No error log file found yet")


def main():
    """Main application function"""
    print("ERROR HANDLING AND DEBUGGING MASTERY")
    print("Error Logger Tool - Track and log user input errors")

    # Initialize error logging system
    error_logger = ErrorLogger()
    calculator = Calculator(error_logger)
    validator = InputValidator(error_logger)

    while True:
        print("\n" + "="*50)
        print("MAIN MENU")
        print("="*50)
        print("1. Input Validation Demo")
        print("2. Calculator with Error Handling")
        print("3. Exception Hierarchy Demo")
        print("4. Debugging Demonstration")
        print("5. View Error Log")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        try:
            if choice == '1':
                print("\n--- INPUT VALIDATION DEMO ---")

                # Integer validation
                int_input = input("Enter a positive integer: ")
                try:
                    valid_int = validator.validate_integer(int_input)
                    print(f"Valid integer: {valid_int}")
                except ValidationError as e:
                    print(f"Validation failed: {e.message}")

                # String validation
                str_input = input("Enter a string (1-100 chars): ")
                try:
                    valid_str = validator.validate_string(str_input)
                    print(f"Valid string: '{valid_str}'")
                except ValidationError as e:
                    print(f"Validation failed: {e.message}")

            elif choice == '2':
                print("\n--- CALCULATOR WITH ERROR HANDLING ---")
                print("1. Division")
                print("2. Power Calculation")

                calc_choice = input("Choose operation (1-2): ").strip()

                if calc_choice == '1':
                    num1 = input("Enter numerator: ")
                    num2 = input("Enter denominator: ")
                    try:
                        result = calculator.safe_divide(num1, num2)
                        print(f"Result: {result}")
                    except (CalculationError, ValidationError) as e:
                        print(f"Calculation error: {e}")

                elif calc_choice == '2':
                    base = input("Enter base: ")
                    exponent = input("Enter exponent: ")
                    try:
                        result = calculator.calculate_power(base, exponent)
                        print(f"Result: {result}")
                    except (CalculationError, ValidationError) as e:
                        print(f"Calculation error: {e}")

                else:
                    print("Invalid calculator choice")

            elif choice == '3':
                demonstrate_exception_hierarchy()

            elif choice == '4':
                interactive_debugging_demo()

            elif choice == '5':
                view_error_log()

            elif choice == '6':
                print("Thank you for using the Error Logger Tool!")
                break

            else:
                print("Invalid choice. Please enter a number between 1-6.")

        except KeyboardInterrupt:
            print("\n\nOperation cancelled by user")
            error_logger.log_error("KeyboardInterrupt",
                                   "User interrupted operation")
            break

        except Exception as e:
            error_logger.log_error(
                "UnexpectedMainError",
                f"Unexpected error in main: {str(e)}"
            )
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
