"""
Python Learning Journey - Day Nine
Date: September 30, 2025
Author: Cosmas Onyekwelu
Topic: Mastery of Conditional Statements & Loop Constructs.
"""


class ConditionalMastery:
    """Advanced conditional statement implementations"""

    def demonstrate_conditionals(self):
        """Comprehensive conditional statements with multiple branches"""
        print("=" * 60)
        print("Conditional Statements Mastery")
        print("=" * 60)

        # Basic if/elif/else structure
        score = 85
        print(f"Score: {score}")

        if score >= 90:
            grade = "A"
            message = "Excellent work!"
        elif score >= 80:
            grade = "B"
            message = "Good job!"
        elif score >= 70:
            grade = "C"
            message = "Satisfactory"
        elif score >= 60:
            grade = "D"
            message = "Needs improvement"
        else:
            grade = "F"
            message = "Please seek help"

        print(f"Grade: {grade}")
        print(f"Message: {message}")

        # Complex conditions with logical operators
        age = 25
        has_license = True
        has_car = False

        print(f"\nAge: {age}, License: {has_license}, Car: {has_car}")

        if age >= 18 and has_license:
            if has_car:
                print("Can drive independently")
            else:
                print("Can drive but needs a vehicle")
        elif age >= 16 and has_license:
            print("Can drive with restrictions")
        else:
            print("Cannot drive")

    def demonstrate_logical_operators(self):
        """Logical operators in complex conditions"""
        print("\n" + "=" * 60)
        print("Logical Operators")
        print("=" * 60)

        # AND operator
        temperature = 22
        is_sunny = True
        is_weekend = False

        if temperature > 20 and is_sunny:
            print("Great weather for outdoor activities")

        # OR operator
        if is_weekend or temperature > 25:
            print("Good time for relaxation")

        # NOT operator
        is_raining = False
        if not is_raining:
            print("No need for an umbrella")

        # Combined conditions
        budget = 100
        item_price = 75
        is_essential = True
        has_discount = True

        if (budget >= item_price and is_essential) or (has_discount and budget >= item_price * 0.5):
            print("You can buy this item")
        else:
            print("Consider your purchase carefully")

    def demonstrate_comparison_operators(self):
        """Comparison operators for data validation"""
        print("\n" + "=" * 60)
        print("Comparison Operators")
        print("=" * 60)

        # Numeric comparisons
        x = 10
        y = 20

        print(f"x = {x}, y = {y}")
        print(f"x == y: {x == y}")
        print(f"x != y: {x != y}")
        print(f"x < y: {x < y}")
        print(f"x > y: {x > y}")
        print(f"x <= y: {x <= y}")
        print(f"x >= y: {x >= y}")

        # String comparisons
        name1 = "Alice"
        name2 = "Bob"

        print(f"\nname1 = '{name1}', name2 = '{name2}'")
        print(f"name1 == name2: {name1 == name2}")
        print(f"name1 != name2: {name1 != name2}")
        print(f"name1 < name2: {name1 < name2}")  # Alphabetical comparison


class LoopMastery:
    """Advanced loop implementations and patterns"""

    def demonstrate_for_loops(self):
        """Comprehensive for loop patterns"""
        print("\n" + "=" * 60)
        print("For Loops")
        print("=" * 60)

        # Basic range loop
        print("Counting 1 to 5:")
        for i in range(1, 6):
            print(f"  Number: {i}")

        # Range with step
        print("\nEven numbers 0 to 10:")
        for i in range(0, 11, 2):
            print(f"  Even: {i}")

        # Looping through lists
        fruits = ["apple", "banana", "cherry", "date"]
        print("\nFruits list:")
        for fruit in fruits:
            print(f"  Fruit: {fruit}")

        # Enumerate for index and value
        print("\nFruits with index:")
        for index, fruit in enumerate(fruits):
            print(f"  {index + 1}. {fruit}")

    def demonstrate_while_loops(self):
        """While loops with various termination conditions"""
        print("\n" + "=" * 60)
        print("While Loops")
        print("=" * 60)

        # Basic counter while loop
        print("Countdown from 5:")
        counter = 5
        while counter > 0:
            print(f"  Count: {counter}")
            counter -= 1
        print("  Liftoff!")

        # While loop with user input
        print("\nInput validation example:")
        valid_input = False
        attempts = 0
        max_attempts = 3

        while not valid_input and attempts < max_attempts:
            user_input = input("Enter 'yes' or 'no': ").lower()
            if user_input in ['yes', 'no']:
                valid_input = True
                print(f"  Valid input received: {user_input}")
            else:
                attempts += 1
                print(
                    f"  Invalid input. Attempts left: {max_attempts - attempts}")

        if not valid_input:
            print("  Maximum attempts reached.")

    def demonstrate_loop_control(self):
        """Break, continue, and pass statements"""
        print("\n" + "=" * 60)
        print("Loop Control Statements")
        print("=" * 60)

        # Break statement
        print("Break example (stop at 5):")
        for i in range(1, 11):
            if i == 6:
                break
            print(f"  Number: {i}")

        # Continue statement
        print("\nContinue example (skip even numbers):")
        for i in range(1, 11):
            if i % 2 == 0:
                continue
            print(f"  Odd number: {i}")

        # Pass statement
        print("\nPass example (placeholder for future code):")
        for i in range(1, 4):
            if i == 2:
                pass  # TODO: Add specific logic later
            print(f"  Processing: {i}")

        # Nested loops with control
        print("\nNested loops with break:")
        for i in range(1, 4):
            for j in range(1, 4):
                if i * j > 4:
                    print(f"  Breaking inner loop at i={i}, j={j}")
                    break
                print(f"  i={i}, j={j}, product={i*j}")


class PracticeExercises:
    """Practice problems for conditionals and loops"""

    def fizz_buzz(self, n):
        """
        Classic FizzBuzz problem
        Print numbers 1 to n, but:
        - Multiples of 3: "Fizz"
        - Multiples of 5: "Buzz" 
        - Multiples of both: "FizzBuzz"
        """
        print(f"\nFizzBuzz for numbers 1 to {n}:")
        for i in range(1, n + 1):
            if i % 15 == 0:
                print("FizzBuzz")
            elif i % 3 == 0:
                print("Fizz")
            elif i % 5 == 0:
                print("Buzz")
            else:
                print(i)

    def number_guessing_game(self):
        """
        Interactive number guessing game
        Computer picks random number, user guesses with hints
        """
        import random

        print("\n" + "=" * 50)
        print("Number Guessing Game")
        print("=" * 50)

        # Game setup
        lower_bound = 1
        upper_bound = 100
        secret_number = random.randint(lower_bound, upper_bound)
        max_attempts = 7
        attempts = 0

        print(
            f"I'm thinking of a number between {lower_bound} and {upper_bound}")
        print(f"You have {max_attempts} attempts to guess it!")

        # Game loop
        while attempts < max_attempts:
            try:
                guess = int(
                    input(f"\nAttempt {attempts + 1}/{max_attempts}. Enter your guess: "))
                attempts += 1

                if guess == secret_number:
                    print(
                        f"Congratulations! You guessed the number in {attempts} attempts!")
                    return
                elif guess < secret_number:
                    print("Too low! Try a higher number.")
                else:
                    print("Too high! Try a lower number.")

                # Give additional hint after a few attempts
                if attempts == max_attempts - 1:
                    if secret_number % 2 == 0:
                        print("Hint: The number is even.")
                    else:
                        print("Hint: The number is odd.")

            except ValueError:
                print("Please enter a valid number!")
                continue

        print(f"\nGame over! The number was {secret_number}.")
        print("Better luck next time!")

    def grade_calculator(self):
        """Calculate letter grades based on score ranges"""
        print("\n" + "=" * 50)
        print("Grade Calculator")
        print("=" * 50)

        scores = [92, 78, 85, 64, 97, 55, 88, 72, 100, 81]

        print("Score to Grade Conversion:")
        for score in scores:
            if score >= 90:
                grade = "A"
            elif score >= 80:
                grade = "B"
            elif score >= 70:
                grade = "C"
            elif score >= 60:
                grade = "D"
            else:
                grade = "F"

            print(f"  Score: {score:3d} -> Grade: {grade}")

    def prime_number_checker(self):
        """Check if numbers are prime using loops and conditions"""
        print("\n" + "=" * 50)
        print("Prime Number Checker")
        print("=" * 50)

        numbers_to_check = [2, 3, 4, 5, 7, 11, 13, 15, 17, 20, 23, 29]

        print("Prime Number Verification:")
        for num in numbers_to_check:
            is_prime = True

            if num < 2:
                is_prime = False
            else:
                # Check divisibility from 2 to square root of num
                for i in range(2, int(num ** 0.5) + 1):
                    if num % i == 0:
                        is_prime = False
                        break

            status = "Prime" if is_prime else "Not Prime"
            print(f"  {num:2d} -> {status}")


def main():
    """Main execution function"""
    print("DAY 9: ADVANCED CONDITIONALS & LOOPS")
    print("=" * 70)

    # Initialize classes
    conditional_master = ConditionalMastery()
    loop_master = LoopMastery()
    exercises = PracticeExercises()

    # Demonstrate conditional concepts
    conditional_master.demonstrate_conditionals()
    conditional_master.demonstrate_logical_operators()
    conditional_master.demonstrate_comparison_operators()

    # Demonstrate loop concepts
    loop_master.demonstrate_for_loops()
    loop_master.demonstrate_while_loops()
    loop_master.demonstrate_loop_control()

    # Practice exercises
    print("\n" + "=" * 70)
    print("PRACTICE EXERCISES")
    print("=" * 70)

    exercises.fizz_buzz(20)
    exercises.grade_calculator()
    exercises.prime_number_checker()

    # Uncomment to play the interactive game
    # exercises.number_guessing_game()


if __name__ == "__main__":
    main()
