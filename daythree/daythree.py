"""
Python Learning Journey - Day Three
Date: September 24, 2025
Author: Cosmas Onyekwelu
Topic: Practicing 10 Important Python Concepts
Based on YouTube tutorial - Core Python fundamentals
"""

# 1. Creating and running Python files
# This file itself demonstrates the concept - save as daythree.py and run with: python daythree.py

# 2. Variables and basic assignment
name = "Cosmas"
age = 25
is_student = True

# 3. Understanding basic data types
integer_example = 42
float_example = 3.14
string_example = "Hello, Python!"
boolean_example = False

# 4. Working with collections
fruits = ["apple", "banana", "cherry"]          # List - mutable and ordered
coordinates = (10, 20)                          # Tuple - immutable and ordered
# Set - unique elements, unordered
unique_numbers = {1, 2, 3, 3}
# Dictionary - key-value pairs
person_info = {"name": "Cosmas", "role": "student"}

# 5. Using type annotations for better code clarity


def square(number: int) -> int:
    return number * number


# 6. Defining constants
PI = 3.14159
MAX_USERS = 100

# 7. Functions with parameters and return types


def greet(person: str, years: int) -> str:
    return f"Hello {person}, you are {years} years old."

# 8. Classes and constructors


class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def introduce(self) -> str:
        return f"My name is {self.name}, and I am {self.age} years old."

# 9. Special dunder methods


class AdvancedStudent(Student):
    def __str__(self) -> str:
        return f"AdvancedStudent(name={self.name}, age={self.age})"

    def __add__(self, other: "AdvancedStudent") -> int:
        # Adds ages of two students
        return self.age + other.age

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, AdvancedStudent):
            return False
        return self.name == other.name and self.age == other.age


# 10. Main execution block for clean, reusable code
if __name__ == "__main__":
    print("=== Python Fundamentals Demonstration ===")

    # Variables and basic types
    print(f"\n1. Variables:")
    print(f"   Name: {name}, Age: {age}, Student: {is_student}")

    # Data types
    print(f"\n2. Data Types:")
    print(f"   Integer: {integer_example}")
    print(f"   Float: {float_example}")
    print(f"   String: {string_example}")
    print(f"   Boolean: {boolean_example}")

    # Collections
    print(f"\n3. Collections:")
    print(f"   Fruits list: {fruits}")
    print(f"   Coordinates tuple: {coordinates}")
    print(f"   Unique numbers set: {unique_numbers}")
    print(f"   Person info dictionary: {person_info}")

    # Functions
    print(f"\n4. Functions:")
    print(f"   Square of 5: {square(5)}")
    print(f"   Greeting: {greet(name, age)}")

    # Constants
    print(f"\n5. Constants:")
    print(f"   PI: {PI}")
    print(f"   MAX_USERS: {MAX_USERS}")

    # Classes
    print(f"\n6. Classes:")
    student1 = Student("Alice", 20)
    print(f"   Student introduction: {student1.introduce()}")

    # Advanced features
    print(f"\n7. Advanced Features:")
    adv1 = AdvancedStudent("Bob", 22)
    adv2 = AdvancedStudent("Charlie", 23)
    print(f"   String representation: {adv1}")
    print(f"   Combined age: {adv1 + adv2}")
    print(f"   Equality check: {adv1 == adv2}")

    print("\n=== All concepts demonstrated successfully! ===")
