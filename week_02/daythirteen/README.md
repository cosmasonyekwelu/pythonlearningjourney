# Day 13: Introduction to Object-Oriented Programming (OOP)

**Date:** October 4, 2025

## Learning Objective
To understand the fundamentals of Object-Oriented Programming, including class definitions, object instantiation, and the difference between class and instance attributes.

## Concepts Covered
- **The Four Pillars of OOP**: Encapsulation, Abstraction, Inheritance, and Polymorphism.
- **Classes vs Objects**: Blueprint versus the individual instance.
- **The Constructor (`__init__`)**: Initializing object state.
- **Instance Methods**: Functions that operate on a specific instance (`self`).
- **Class Attributes & Methods**: Shared data and behavior at the class level.
- **Private Methods**: Using the `_` prefix for internal logic (convention).

## Code Explanation
The `day_thirteen.py` script introduces OOP through relatable examples:
- **OOPFundamentals**: A conceptual overview of why we use OOP (modularity, reusability).
- **Person & Student Classes**: Demonstrates basic initialization, instance methods, and using methods to update an object's state (e.g., `have_birthday`, `enroll`).
- **Bank Class**: Shows class-level attributes (`bank_name`, `total_accounts`) and how they differ from instance-level data like `balance`.
- **PracticeExercises**:
    - `Rectangle`: A geometric class for calculating area and perimeter.
    - `SimpleBankAccount`: A preview of a larger project, focusing on recording transactions and managing balance.

## How to Run
Execute the script to see the OOP demonstrations:
```bash
python week_02/daythirteen/day_thirteen.py
```

## Reflection
OOP is a powerful way to organize code by thinking in terms of "things" and "actions". It makes managing complex systems much more intuitive by grouping related data and logic together.
