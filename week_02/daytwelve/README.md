# Day 12: Functions, Scope & Error Handling

**Date:** October 3, 2025

## Learning Objective
To master function definitions, parameter passing (including `*args` and `**kwargs`), variable scope (global/nonlocal), and robust error handling using try/except blocks.

## Concepts Covered
- **Function Parameters**: Positional, keyword, default, and arbitrary arguments (`*args`, `**kwargs`).
- **Variable Scope**: Understanding Local, Global, and Nonlocal scopes.
- **Exception Handling**: Basic and advanced `try/except/else/finally` patterns.
- **Custom Exceptions**: Creating user-defined exception classes for specific error scenarios.
- **Closures**: Using nested functions and the `nonlocal` keyword for state persistence.
- **Data Validation**: Implementing robust input checking and custom validation errors.

## Code Explanation
The `day_twelve.py` script is a comprehensive guide to functions and errors:
- **FunctionFundamentals**: Demonstrates everything from basic type hints to complex `**kwargs` usage and global variable management.
- **ExceptionHandling**: Shows how to catch multiple exceptions and use `finally` for cleanup (like closing files).
- **Custom Exceptions**: Defines `CalculatorError` and its subclasses to show how to build an informative error hierarchy.
- **PracticeExercises**:
    - `robust_calculator`: A command-line calculator that handles invalid inputs and math errors gracefully.
    - `create_counter`: Demonstrates closures and `nonlocal` scope to create independent counter objects.
    - `validate_user_profile`: A practical example of multi-step data validation.

## How to Run
Run the script to see the function and exception demonstrations:
```bash
python week_02/daytwelve/day_twelve.py
```

## Reflection
Error handling is what separates a script from a professional application. Custom exceptions allow you to communicate exactly what went wrong, and understanding scope is vital for avoiding bugs in complex programs.
