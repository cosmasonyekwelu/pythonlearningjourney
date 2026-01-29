# Day 20: Modules and Packages

**Date:** October 11, 2025

## Learning Objective
To understand how to organize code into modules and packages, and how to use Python's built-in and external libraries effectively.

## Concepts Covered
- **Built-in Modules**: Using `math`, `datetime`, `os`, `sys`, `random`, and `json`.
- **Custom Modules**: Creating and importing your own `.py` files (`file_utils.py`, `math_utils.py`).
- **Packages**: Organizing multiple modules into directories.
- **External Packages**: Managing dependencies with `pip` and `requirements.txt`.
- **Virtual Environments**: Understanding the importance of `venv` for project isolation.
- **Try-Except Imports**: Handling missing dependencies gracefully.

## Code Explanation
The `day_twenty.py` script serves as a hub for various utility functions:
- **`demonstrate_builtin_modules()`**: Showcases math constants, current time formatting, and system platform detection.
- **`demonstrate_file_operations()`**: Uses functions from the custom `file_utils` module to manage JSON and text data.
- **`demonstrate_math_operations()`**: Uses the custom `math_utils` module for statistical calculations and geometry.
- **`virtual_environment_info()`**: Checks if the script is currently running inside an isolated environment.

## How to Run
Ensure `file_utils.py` and `math_utils.py` are in the same directory as the main script:
```bash
python week_03/daytwenty/day_twenty.py
```

## Reflection
Modularization is key to scaling applications. By breaking code into separate files (modules), you make it reusable and easier for teams to collaborate on different parts of a project.
