"""
Day 12: Functions, Scope & Errors
Python Learning Journey - Comprehensive Function and Error Handling Concepts
"""


class FunctionFundamentals:
    """Function definitions, parameters, and scope management"""
    
    def demonstrate_function_basics(self):
        """Basic function concepts and parameter types"""
        print("=" * 60)
        print("Function Fundamentals")
        print("=" * 60)
        
        # Basic function with parameters
        def greet(name, greeting="Hello"):
            return f"{greeting}, {name}!"
        
        print(f"Basic function: {greet('Alice')}")
        print(f"With custom greeting: {greet('Bob', 'Hi')}")
        
        # Function with multiple return values
        def calculate_circle(radius):
            import math
            area = math.pi * radius ** 2
            circumference = 2 * math.pi * radius
            return area, circumference
        
        area, circ = calculate_circle(5)
        print(f"Circle with radius 5: Area={area:.2f}, Circumference={circ:.2f}")
        
        # Type hints (Python 3.5+)
        def add_numbers(a: int, b: int) -> int:
            return a + b
        
        result = add_numbers(10, 20)
        print(f"Typed function result: {result}")
    
    def demonstrate_parameter_types(self):
        """Different function parameter patterns"""
        print("\n" + "=" * 60)
        print("Function Parameter Types")
        print("=" * 60)
        
        # Positional arguments
        def describe_pet(animal_type, pet_name):
            return f"I have a {animal_type} named {pet_name}."
        
        print(f"Positional args: {describe_pet('dog', 'Rex')}")
        
        # Keyword arguments
        print(f"Keyword args: {describe_pet(pet_name='Whiskers', animal_type='cat')}")
        
        # Default parameters
        def make_shirt(size='large', message='I love Python'):
            return f"Shirt size: {size}, Message: {message}"
        
        print(f"Default params: {make_shirt()}")
        print(f"Custom params: {make_shirt('medium', 'Hello World')}")
        
        # Arbitrary arguments (*args)
        def make_pizza(*toppings):
            return f"Pizza with: {', '.join(toppings)}"
        
        print(f"Arbitrary args: {make_pizza('pepperoni', 'mushrooms', 'cheese')}")
        
        # Arbitrary keyword arguments (**kwargs)
        def build_profile(first, last, **user_info):
            profile = {'first_name': first, 'last_name': last}
            profile.update(user_info)
            return profile
        
        user_profile = build_profile('John', 'Doe', age=30, city='NYC', occupation='Engineer')
        print(f"Arbitrary kwargs: {user_profile}")
    
    def demonstrate_scope_concepts(self):
        """Variable scope: local, global, and nonlocal"""
        print("\n" + "=" * 60)
        print("Variable Scope")
        print("=" * 60)
        
        # Global variable
        global_var = "I am global"
        
        def test_local_scope():
            # Local variable
            local_var = "I am local"
            print(f"Inside function - local_var: {local_var}")
            
            # Accessing global variable (read-only)
            print(f"Inside function - global_var: {global_var}")
            
            def inner_function():
                # Nonlocal variable
                nonlocal local_var
                local_var = "Modified by inner function"
                print(f"Inner function - local_var: {local_var}")
            
            inner_function()
            return local_var
        
        result = test_local_scope()
        print(f"After function - global_var: {global_var}")
        print(f"After function - result: {result}")
        
        # Demonstrating global keyword
        counter = 0
        
        def increment_counter():
            global counter
            counter += 1
            return counter
        
        print(f"\nGlobal counter: {increment_counter()}")
        print(f"Global counter: {increment_counter()}")
        print(f"Global counter: {increment_counter()}")


class ExceptionHandling:
    """Comprehensive exception handling techniques"""
    
    def demonstrate_basic_exception_handling(self):
        """Basic try/except patterns"""
        print("\n" + "=" * 60)
        print("Basic Exception Handling")
        print("=" * 60)
        
        # Basic try/except
        def safe_divide(a, b):
            try:
                result = a / b
                return result
            except ZeroDivisionError:
                return "Error: Cannot divide by zero"
        
        print(f"Safe divide 10/2: {safe_divide(10, 2)}")
        print(f"Safe divide 10/0: {safe_divide(10, 0)}")
        
        # Multiple exception types
        def process_number(value):
            try:
                number = float(value)
                return f"Processed: {number}"
            except (ValueError, TypeError):
                return f"Error: Cannot convert '{value}' to number"
        
        print(f"Process '123': {process_number('123')}")
        print(f"Process 'abc': {process_number('abc')}")
        print(f"Process None: {process_number(None)}")
        
        # Getting exception information
        def analyze_data(data):
            try:
                if not data:
                    raise ValueError("Data cannot be empty")
                return f"Data analysis: {sum(data) / len(data)}"
            except Exception as e:
                return f"Analysis failed: {type(e).__name__}: {e}"
        
        print(f"Analyze [1,2,3]: {analyze_data([1, 2, 3])}")
        print(f"Analyze empty: {analyze_data([])}")
    
    def demonstrate_advanced_exception_handling(self):
        """Advanced exception handling patterns"""
        print("\n" + "=" * 60)
        print("Advanced Exception Handling")
        print("=" * 60)
        
        # Try/except/else/finally
        def read_config_file(filename):
            try:
                file = open(filename, 'r')
                print(f"Successfully opened {filename}")
            except FileNotFoundError:
                print(f"Error: File '{filename}' not found")
                return None
            except PermissionError:
                print(f"Error: Permission denied for '{filename}'")
                return None
            else:
                try:
                    content = file.read()
                    return f"Config content: {content.strip()}"
                except Exception as e:
                    print(f"Error reading file: {e}")
                    return None
                finally:
                    file.close()
                    print("File closed successfully")
            finally:
                print(f"Completed file operation for: {filename}")
        
        # Test with non-existent file
        result = read_config_file("nonexistent.config")
        print(f"Result: {result}")
        
        # Handling multiple specific exceptions
        def robust_calculation(operation, *args):
            try:
                if operation == 'divide':
                    return args[0] / args[1]
                elif operation == 'power':
                    return args[0] ** args[1]
                elif operation == 'sqrt':
                    if args[0] < 0:
                        raise ValueError("Cannot calculate square root of negative number")
                    return args[0] ** 0.5
                else:
                    raise ValueError(f"Unknown operation: {operation}")
            
            except ZeroDivisionError:
                return "Error: Division by zero"
            except ValueError as e:
                return f"Error: {e}"
            except TypeError:
                return "Error: Invalid input types"
            except IndexError:
                return "Error: Insufficient arguments"
    
    def demonstrate_custom_exceptions(self):
        """Creating and using custom exceptions"""
        print("\n" + "=" * 60)
        print("Custom Exceptions")
        print("=" * 60)
        
        # Custom exception class
        class CalculatorError(Exception):
            """Base exception for calculator operations"""
            pass
        
        class DivisionByZeroError(CalculatorError):
            def __init__(self, operation):
                super().__init__(f"Cannot perform {operation} by zero")
        
        class NegativeNumberError(CalculatorError):
            def __init__(self, operation, value):
                super().__init__(f"Cannot perform {operation} on negative number: {value}")
        
        class InvalidInputError(CalculatorError):
            def __init__(self, input_value, expected_type):
                super().__init__(f"Invalid input: {input_value}. Expected {expected_type}")
        
        # Using custom exceptions
        def safe_square_root(number):
            if not isinstance(number, (int, float)):
                raise InvalidInputError(number, "number")
            if number < 0:
                raise NegativeNumberError("square root", number)
            return number ** 0.5
        
        def safe_divide_custom(a, b):
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise InvalidInputError(f"({a}, {b})", "numbers")
            if b == 0:
                raise DivisionByZeroError("division")
            return a / b
        
        # Test custom exceptions
        test_cases = [
            (16, "valid square root"),
            (-4, "negative square root"),
            ("string", "invalid input"),
            (10, 2, "valid division"),
            (10, 0, "division by zero")
        ]
        
        for case in test_cases:
            try:
                if len(case) == 2:
                    result = safe_square_root(case[0])
                    print(f"{case[1]}: {result}")
                else:
                    result = safe_divide_custom(case[0], case[1])
                    print(f"{case[2]}: {result}")
            except CalculatorError as e:
                print(f"{case[-1]}: {e}")


class PracticeExercises:
    """Practice problems for functions and error handling"""
    
    def create_robust_calculator(self):
        """Interactive calculator with comprehensive error handling"""
        print("\n" + "=" * 50)
        print("Robust Calculator")
        print("=" * 50)
        
        # Custom exceptions for calculator
        class CalculatorException(Exception):
            pass
        
        class InvalidOperatorError(CalculatorException):
            pass
        
        class CalculationError(CalculatorException):
            pass
        
        def get_number_input(prompt):
            """Safely get number input from user"""
            while True:
                try:
                    value = input(prompt)
                    if value.lower() == 'quit':
                        return None
                    return float(value)
                except ValueError:
                    print("Error: Please enter a valid number or 'quit' to exit")
        
        def perform_calculation(num1, num2, operator):
            """Perform calculation with error handling"""
            try:
                if operator == '+':
                    return num1 + num2
                elif operator == '-':
                    return num1 - num2
                elif operator == '*':
                    return num1 * num2
                elif operator == '/':
                    if num2 == 0:
                        raise ZeroDivisionError("Division by zero")
                    return num1 / num2
                elif operator == '**':
                    return num1 ** num2
                elif operator == '//':
                    if num2 == 0:
                        raise ZeroDivisionError("Integer division by zero")
                    return num1 // num2
                elif operator == '%':
                    if num2 == 0:
                        raise ZeroDivisionError("Modulo by zero")
                    return num1 % num2
                else:
                    raise InvalidOperatorError(f"Unknown operator: {operator}")
            
            except ZeroDivisionError as e:
                raise CalculationError(f"Math error: {e}")
            except OverflowError:
                raise CalculationError("Result too large")
            except Exception as e:
                raise CalculationError(f"Unexpected error: {e}")
        
        def calculator_interface():
            """Main calculator interface"""
            print("Welcome to the Safe Calculator!")
            print("Available operations: +, -, *, /, **, //, %")
            print("Enter 'quit' at any time to exit")
            
            while True:
                try:
                    # Get first number
                    num1 = get_number_input("\nEnter first number: ")
                    if num1 is None:
                        break
                    
                    # Get operator
                    operator = input("Enter operator (+, -, *, /, **, //, %): ")
                    if operator.lower() == 'quit':
                        break
                    
                    # Get second number
                    num2 = get_number_input("Enter second number: ")
                    if num2 is None:
                        break
                    
                    # Perform calculation
                    result = perform_calculation(num1, num2, operator)
                    print(f"Result: {num1} {operator} {num2} = {result}")
                
                except (InvalidOperatorError, CalculationError) as e:
                    print(f"Calculation error: {e}")
                except KeyboardInterrupt:
                    print("\nCalculator stopped by user")
                    break
                except Exception as e:
                    print(f"Unexpected error: {e}")
            
            print("Thank you for using the Safe Calculator!")
        
        # Run the calculator
        calculator_interface()
    
    def demonstrate_data_validation(self):
        """Data validation with comprehensive error handling"""
        print("\n" + "=" * 50)
        print("Data Validation Functions")
        print("=" * 50)
        
        class ValidationError(Exception):
            pass
        
        class AgeValidationError(ValidationError):
            pass
        
        class EmailValidationError(ValidationError):
            pass
        
        def validate_age(age):
            """Validate age with proper error handling"""
            try:
                age_int = int(age)
                if age_int < 0:
                    raise AgeValidationError("Age cannot be negative")
                if age_int > 150:
                    raise AgeValidationError("Age seems unrealistic")
                return age_int
            except ValueError:
                raise AgeValidationError("Age must be a valid number")
        
        def validate_email(email):
            """Validate email format"""
            if not isinstance(email, str):
                raise EmailValidationError("Email must be a string")
            
            email = email.strip()
            if '@' not in email:
                raise EmailValidationError("Email must contain '@'")
            
            local_part, domain = email.split('@', 1)
            if not local_part or not domain:
                raise EmailValidationError("Invalid email format")
            
            if '.' not in domain:
                raise EmailValidationError("Domain must contain '.'")
            
            return email.lower()
        
        def validate_user_profile(profile_data):
            """Validate complete user profile"""
            errors = []
            validated_data = {}
            
            # Validate name
            try:
                name = profile_data.get('name', '').strip()
                if not name:
                    errors.append("Name is required")
                else:
                    validated_data['name'] = name
            except Exception as e:
                errors.append(f"Name validation error: {e}")
            
            # Validate age
            try:
                age = validate_age(profile_data.get('age', 0))
                validated_data['age'] = age
            except AgeValidationError as e:
                errors.append(f"Age error: {e}")
            except Exception as e:
                errors.append(f"Unexpected age error: {e}")
            
            # Validate email
            try:
                email = validate_email(profile_data.get('email', ''))
                validated_data['email'] = email
            except EmailValidationError as e:
                errors.append(f"Email error: {e}")
            except Exception as e:
                errors.append(f"Unexpected email error: {e}")
            
            return validated_data, errors
        
        # Test validation functions
        test_profiles = [
            {'name': 'Alice', 'age': '25', 'email': 'alice@example.com'},
            {'name': 'Bob', 'age': '-5', 'email': 'bob@example.com'},
            {'name': '', 'age': '30', 'email': 'invalid-email'},
            {'name': 'Charlie', 'age': 'two hundred', 'email': 'charlie@test.co.uk'}
        ]
        
        for i, profile in enumerate(test_profiles, 1):
            print(f"\nTest Profile {i}: {profile}")
            validated, errors = validate_user_profile(profile)
            
            if errors:
                print(f"  Validation errors: {errors}")
            else:
                print(f"  Validated data: {validated}")
    
    def demonstrate_scope_exercises(self):
        """Scope-related practice exercises"""
        print("\n" + "=" * 50)
        print("Scope Practice Exercises")
        print("=" * 50)
        
        # Exercise 1: Counter with closure
        def create_counter(initial_value=0):
            count = initial_value
            
            def increment(step=1):
                nonlocal count
                count += step
                return count
            
            def decrement(step=1):
                nonlocal count
                count -= step
                return count
            
            def get_value():
                return count
            
            def reset():
                nonlocal count
                count = initial_value
                return count
            
            return increment, decrement, get_value, reset
        
        # Create counters
        inc1, dec1, get1, reset1 = create_counter(10)
        inc2, dec2, get2, reset2 = create_counter(100)
        
        print("Counter 1 (starts at 10):")
        print(f"  Increment: {inc1()} -> {inc1(5)}")
        print(f"  Decrement: {dec1()} -> {dec1(2)}")
        print(f"  Current: {get1()}")
        print(f"  After reset: {reset1()}")
        
        print("\nCounter 2 (starts at 100):")
        print(f"  Increment: {inc2(10)} -> {inc2(20)}")
        print(f"  Current: {get2()}")
        
        # Exercise 2: Function factory for math operations
        def create_math_operations():
            operations = {}
            
            def add_operation(name, func):
                operations[name] = func
            
            def perform_operation(name, *args):
                if name not in operations:
                    raise ValueError(f"Unknown operation: {name}")
                return operations[name](*args)
            
            def list_operations():
                return list(operations.keys())
            
            # Add some default operations
            add_operation('add', lambda x, y: x + y)
            add_operation('multiply', lambda x, y: x * y)
            add_operation('power', lambda x, y: x ** y)
            
            return perform_operation, add_operation, list_operations
        
        # Use the math operations factory
        calculate, add_op, list_ops = create_math_operations()
        
        print(f"\nAvailable operations: {list_ops()}")
        print(f"Add: 5 + 3 = {calculate('add', 5, 3)}")
        print(f"Multiply: 5 * 3 = {calculate('multiply', 5, 3)}")
        print(f"Power: 2 ** 8 = {calculate('power', 2, 8)}")
        
        # Add a custom operation
        add_op('average', lambda *args: sum(args) / len(args) if args else 0)
        print(f"Average: {calculate('average', 10, 20, 30, 40)}")


def main():
    """Main execution function"""
    print("DAY 12: FUNCTIONS, SCOPE & ERRORS")
    print("=" * 70)
    
    # Initialize classes
    function_basics = FunctionFundamentals()
    exception_handling = ExceptionHandling()
    practice_exercises = PracticeExercises()
    
    # Demonstrate function concepts
    function_basics.demonstrate_function_basics()
    function_basics.demonstrate_parameter_types()
    function_basics.demonstrate_scope_concepts()
    
    # Demonstrate exception handling
    exception_handling.demonstrate_basic_exception_handling()
    exception_handling.demonstrate_advanced_exception_handling()
    exception_handling.demonstrate_custom_exceptions()
    
    # Practice exercises
    print("\n" + "=" * 70)
    print("PRACTICE EXERCISES")
    print("=" * 70)
    
    practice_exercises.demonstrate_data_validation()
    practice_exercises.demonstrate_scope_exercises()
    
    # Uncomment to run interactive calculator
    # practice_exercises.create_robust_calculator()


if __name__ == "__main__":
    main()