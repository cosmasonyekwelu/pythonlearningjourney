# Day 19: Error Handling and Debugging Mastery

**Date:** October 10, 2025

## Learning Objective
To master sophisticated error handling techniques, logging, and debugging strategies for building resilient applications.

## Concepts Covered
- **Custom Exceptions**: Creating specialized exception classes (`ValidationError`, `CalculationError`) to improve error clarity.
- **Logging**: Using the `logging` module to track application events, errors, and info to both the console and a file.
- **Exception Chaining**: Using `raise ... from e` to preserve original error context.
- **Debugging Tools**: Introduction to the Python Debugger (`pdb`) and using `traceback` for error analysis.
- **Interactive Menu Systems**: Building robust CLI interfaces with persistent error logging.

## Code Explanation
The `day_nineteen.py` script is a high-level demonstration of defensive programming:
- **ErrorLogger Class**: Configures a professional logging system that outputs to `error_log.txt`.
- **InputValidator Class**: Uses try-except blocks to strictly validate strings, integers, and floats, logging failures automatically.
- **Calculator Class**: Implements math operations with checks for edge cases (like division by zero or large overflows) using custom exceptions.
- **`interactive_debugging_demo()`**: Intentionally contains a bug to show how `traceback` can be used to pinpoint logical errors.

## How to Run
Run the interactive menu:
```bash
python week_03/daynineteen/day_nineteen.py
```

## Reflection
Debugging is like being a detective in a crime movie where you are also the murderer. Learning to use logging instead of just `print()` statements and mastering custom exceptions makes your code much easier to maintain and troubleshoot.
