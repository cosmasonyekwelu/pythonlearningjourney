# Day 15: Advanced OOP - Inheritance and Polymorphism

**Date:** October 6, 2025

## Learning Objective
To master the advanced OOP concepts of Inheritance (single and multiple) and Polymorphism, enabling the creation of complex and flexible class hierarchies.

## Concepts Covered
- **Single Inheritance**: Creating a child class that inherits from a single parent.
- **Multiple Inheritance**: Inheriting from multiple parent classes and understanding Method Resolution Order (MRO).
- **Method Overriding**: Providing a specialized implementation of a parent class method in a child class.
- **Using `super()`**: Accessing parent class methods and constructors.
- **Polymorphism**: Using a unified interface to interact with objects of different classes.
- **Type Checking**: Using `isinstance()` and `issubclass()`.

## Code Explanation
The `day_fifteen.py` script demonstrates these concepts through interactive examples:
- **InheritanceFundamentals**: Shows how `Dog` and `Cat` inherit from `Animal`, and how a `HybridVehicle` can inherit from both `Engine` and `ElectricSystem`.
- **Polymorphism Demo**: Shows how different `Shape` objects (Rectangle, Circle, Triangle) all implement `area()` and `perimeter()` differently but can be processed in a single loop.
- **Vehicle Hierarchy Project**: A practical application building a hierarchy from `Vehicle` down to `SportsCar`, illustrating deep inheritance and polymorphic operations.

## How to Run
Execute the script to see the inheritance and polymorphism demonstrations:
```bash
python week_03/dayfifteen/day_fifteen.py
```

## Reflection
Inheritance is essential for code reuse, but Polymorphism is what makes OOP truly powerful. Being able to treat different objects as the same base type allows for much more generic and maintainable code.
