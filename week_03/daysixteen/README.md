# Day 16: Advanced OOP - Encapsulation and Properties

**Date:** October 7, 2025

## Learning Objective
To master Encapsulation in Python, learning how to protect data using private/protected attributes and control access using property decorators.

## Concepts Covered
- **Protected Attributes**: Using the `_` prefix convention for internal-use attributes.
- **Private Attributes**: Using the `__` prefix for name mangling to avoid subclass conflicts.
- **Property Decorators**: Using `@property`, `@setter`, and `@deleter` for controlled attribute access.
- **Data Validation**: Implementing logic within setters to ensure data integrity.
- **Computed Properties**: Creating read-only properties that derive their value from other attributes.

## Code Explanation
The `day_sixteen.py` script explores data protection:
- **EncapsulationFundamentals**: Demonstrates the difference between public, protected, and private members.
- **Temperature Class**: Uses properties to automatically convert between Celsius, Fahrenheit, and Kelvin while validating that temperatures aren't below absolute zero.
- **SecureBankVault**: Shows how private attributes and name mangling prevent accidental external access.
- **Enhanced Bank Account Project**: A comprehensive example using properties to manage balance, overdraft limits, and transaction history with full validation.

## How to Run
Run the script to see encapsulation and property validation in action:
```bash
python week_03/daysixteen/day_sixteen.py
```

## Reflection
Encapsulation isn't just about hiding data; it's about creating a robust interface. Using properties allows you to add validation logic later without changing how other parts of the code access your object's data.
