"""

Python Learning Journey - Day Three
Date: September 24, 2025
Author: Cosmas Onyekwelu
Topic: Based on YouTube tutorial Practicing 10 Important Python Concepts
"""

from typing import Final


# 1. Creating a Python file and running it
# (This file itself is an example — save as daythree.py and run with: python daythree.py)


# 2. Variables & assignment
name: str = "Cosmas"
age: int = 25
is_student: bool = True


# 3. Basic data types
integer_example: int = 42
float_example: float = 3.14
string_example: str = "Hello, Python!"
boolean_example: bool = False


# 4. Collections (list, tuple, set, dict)
fruits: list[str] = ["apple", "banana", "cherry"]   # list (mutable, ordered)
# tuple (immutable, ordered)
coordinates: tuple[int, int] = (10, 20)
unique_numbers: set[int] = {1, 2, 3, 3}             # set (unique, unordered)
person_info: dict[str, str] = {"name": "Cosmas",
                               "role": "student"}  # dict (key-value)


# 5. Type annotations
def square(number: int) -> int:
    return number * number


# 6. Constants (Final)
PI: Final[float] = 3.14159
MAX_USERS: Final[int] = 100


# 7. Functions with parameters and return types
def greet(person: str, years: int) -> str:
    return f"Hello {person}, you are {years} years old."


# 8. Classes & __init__
class Student:
    def __init__(self, name: str, age: int):
        self.name = name
        self.age = age

    def introduce(self) -> str:
        return f"My name is {self.name}, and I am {self.age} years old."


# 9. Dunder (magic) methods
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


# 10. Writing clean, reusable code
if __name__ == "__main__":
    # Variables & types
    print(f"Name: {name}, Age: {age}, Student? {is_student}")

    # Basic data types
    print(
        f"Integer: {integer_example}, Float: {float_example}, String: {string_example}, Bool: {boolean_example}")

    # Collections
    print(f"Fruits: {fruits}")
    print(f"Coordinates: {coordinates}")
    print(f"Unique numbers: {unique_numbers}")
    print(f"Person info: {person_info}")

    # Functions
    print(f"Square of 5: {square(5)}")
    print(greet(name, age))

    # Classes
    student1 = Student("Alice", 20)
    print(student1.introduce())

    # Advanced Student with dunder methods
    adv1 = AdvancedStudent("Bob", 22)
    adv2 = AdvancedStudent("Charlie", 23)
    print(adv1)
    print(f"Combined age (adv1 + adv2): {adv1 + adv2}")
    print(f"Are adv1 and adv2 equal? {adv1 == adv2}")
