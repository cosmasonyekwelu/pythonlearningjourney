# Day 03: Core Python Concepts Deep Dive

**Date:** September 24, 2025

## Learning Objective
To reinforce fundamental Python concepts and explore advanced features like type annotations, classes, and special "dunder" methods.

## Concepts Covered
1. **Variables & Basic Assignment**: Storing data.
2. **Data Types**: Integers, Floats, Strings, Booleans.
3. **Collections**: Lists (mutable), Tuples (immutable), Sets (unique), Dictionaries (key-value).
4. **Type Annotations**: Adding clarity to function signatures.
5. **Constants**: Using uppercase for fixed values.
6. **Functions**: Modularizing code with parameters and returns.
7. **Object-Oriented Programming (OOP)**: Creating classes and constructors.
8. **Inheritance**: Extending classes.
9. **Dunder Methods**: Implementing `__str__`, `__add__`, and `__eq__`.
10. **Main Execution Block**: Using `if __name__ == "__main__":`.

## Code Explanation
The `day_three.py` script provides a practical demonstration of 10 essential Python concepts.
- `square(number: int) -> int`: Demonstrates type hints and basic arithmetic.
- `Student` Class: A base class representing a student with a name and age.
- `AdvancedStudent` Class: Inherits from `Student` and implements:
    - `__str__`: Custom string representation.
    - `__add__`: Allows adding two students together (returns sum of ages).
    - `__eq__`: Compares two students for equality based on name and age.

## How to Run
Run the script using Python:
```bash
python week_01/daythree/day_three.py
```

## Reflection
Moving from basic scripts to Object-Oriented Programming is a big step. Dunder methods are particularly powerful for making custom classes behave like built-in Python types.
