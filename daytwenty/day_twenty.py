"""
Day 20 - Modules and Packages
Utility Toolkit: A helper module for file and math operations

Demonstrates:
- Built-in module usage
- Custom module creation and import
- External package management
- Virtual environments
"""

import math
import datetime
import os
import sys
import random
import json
from typing import List, Dict, Any

# Import custom modules
try:
    from file_utils import (
        create_file, read_file, append_to_file,
        read_json_file, write_json_file, get_file_info,
        list_directory_contents, create_sample_files
    )
    from math_utils import (
        calculate_average, calculate_median, calculate_standard_deviation,
        factorial, is_prime, fibonacci_sequence,
        calculate_circle_area, calculate_circle_circumference,
        solve_quadratic, convert_temperature,
        generate_random_stats, display_math_constants
    )
    print("Custom modules imported successfully.")
except ImportError as e:
    print(f"Error importing custom modules: {e}")
    print("Make sure file_utils.py and math_utils.py are in the same directory.")
    sys.exit(1)


def demonstrate_builtin_modules():
    """Demonstrate usage of Python's built-in modules"""
    print("\n" + "="*60)
    print("BUILT-IN MODULES DEMONSTRATION")
    print("="*60)

    # Math module
    print("\nMATH MODULE:")
    print(f"  π (Pi): {math.pi}")
    print(f"  e (Euler's number): {math.e}")
    print(f"  Square root of 16: {math.sqrt(16)}")
    print(f"  2^8 using pow: {math.pow(2, 8)}")
    print(f"  Cosine of 60°: {math.cos(math.radians(60)):.3f}")

    # Datetime module
    print("\nDATETIME MODULE:")
    now = datetime.datetime.now()
    print(f"  Current date/time: {now}")
    print(f"  Formatted: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Year: {now.year}, Month: {now.month}, Day: {now.day}")

    # OS and SYS module
    print("\nOS AND SYS MODULES:")
    print(f"  Current working directory: {os.getcwd()}")
    print(f"  OS platform: {sys.platform}")
    print(
        f"  Python version: {sys.version_info.major}.{sys.version_info.minor}")

    # Random module
    print("\nRANDOM MODULE:")
    print(f"  Random number (1-100): {random.randint(1, 100)}")
    print(
        f"  Random choice from list: {random.choice(['apple', 'banana', 'cherry'])}")
    print(f"  Random sample: {random.sample(range(1, 50), 5)}")


def demonstrate_file_operations():
    """Demonstrate file utility functions"""
    print("\n" + "="*60)
    print("FILE OPERATIONS DEMONSTRATION")
    print("="*60)

    # Create sample files
    create_sample_files()

    # Read and display file contents
    print("\nFILE READING:")
    text_content = read_file("sample_data/example.txt")
    if text_content:
        print("Text file content:")
        print(text_content)

    # JSON operations
    print("\nJSON OPERATIONS:")
    json_data = read_json_file("sample_data/data.json")
    if json_data:
        print("JSON data:")
        print(json.dumps(json_data, indent=2))

    # File information
    print("\nFILE INFORMATION:")
    file_info = get_file_info("sample_data/example.txt")
    for key, value in file_info.items():
        print(f"  {key}: {value}")

    # Directory listing
    print("\nDIRECTORY LISTING:")
    contents = list_directory_contents("sample_data")
    for item in contents:
        if "error" not in item:
            item_type = "FILE" if item["is_file"] else "DIR"
            size_info = f" ({item.get('size_bytes', 0)} bytes)" if item["is_file"] else ""
            print(f"  {item_type} - {item['name']}{size_info}")


def demonstrate_math_operations():
    """Demonstrate math utility functions"""
    print("\n" + "="*60)
    print("MATH OPERATIONS DEMONSTRATION")
    print("="*60)

    numbers = [23, 45, 67, 12, 89, 34, 56, 78, 90, 11]

    print("\nSTATISTICAL CALCULATIONS:")
    print(f"  Numbers: {numbers}")
    print(f"  Average: {calculate_average(numbers):.2f}")
    print(f"  Median: {calculate_median(numbers)}")
    print(f"  Standard Deviation: {calculate_standard_deviation(numbers):.2f}")

    print("\nNUMBER THEORY:")
    print(f"  Factorial of 7: {factorial(7):,}")
    for num in [17, 25, 29, 100]:
        print(f"  Is {num} prime? {is_prime(num)}")

    print("\nGEOMETRY:")
    radius = 5
    print(f"  Circle with radius {radius}:")
    print(f"    Area: {calculate_circle_area(radius):.2f}")
    print(f"    Circumference: {calculate_circle_circumference(radius):.2f}")

    print("\nTEMPERATURE CONVERSION:")
    conversions = [
        (0, 'C', 'F'),
        (100, 'C', 'F'),
        (98.6, 'F', 'C'),
        (0, 'C', 'K')
    ]
    for temp, from_u, to_u in conversions:
        converted = convert_temperature(temp, from_u, to_u)
        print(f"  {temp}°{from_u} = {converted:.1f}°{to_u}")

    print("\nRANDOM STATISTICS:")
    random_stats = generate_random_stats(8)
    print(
        f"  Generated numbers: {[round(x, 2) for x in random_stats['numbers']]}")
    print(f"  Stats - Avg: {random_stats['average']:.2f}, "
          f"Median: {random_stats['median']:.2f}, "
          f"Std Dev: {random_stats['standard_deviation']:.2f}")


def demonstrate_external_packages():
    """Demonstrate external package usage (if available)"""
    print("\n" + "="*60)
    print("EXTERNAL PACKAGES DEMONSTRATION")
    print("="*60)

    external_packages = []

    try:
        import requests
        external_packages.append("requests - HTTP library")
    except ImportError:
        pass

    try:
        import pandas as pd
        external_packages.append("pandas - Data analysis")
    except ImportError:
        pass

    try:
        import numpy as np
        external_packages.append("numpy - Numerical computing")
    except ImportError:
        pass

    if external_packages:
        print("Installed external packages:")
        for package in external_packages:
            print(f"  - {package}")
    else:
        print("No external packages found.")
        print("You can install them using: pip install -r requirements.txt")


def virtual_environment_info():
    """Display virtual environment information"""
    print("\n" + "="*60)
    print("VIRTUAL ENVIRONMENT INFORMATION")
    print("="*60)

    in_venv = hasattr(sys, 'real_prefix') or (
        hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix
    )

    if in_venv:
        print("Running inside a virtual environment.")
        print(f"  Python executable: {sys.executable}")
        print(f"  Virtual env prefix: {sys.prefix}")
    else:
        print("Not running in a virtual environment.")
        print("You can create one using: python -m venv venv")


def main():
    """Main application function"""
    print("DAY 20 - MODULES AND PACKAGES")
    print("Utility Toolkit - File and Math Operations")
    print("="*60)

    print("\nMODULES LOADED:")
    print("  Built-in: math, datetime, os, sys, random, json")
    print("  Custom: file_utils, math_utils")

    demonstrate_builtin_modules()
    demonstrate_file_operations()
    demonstrate_math_operations()
    demonstrate_external_packages()
    virtual_environment_info()

    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print("Built-in modules demonstrated.")
    print("Custom modules created and imported.")
    print("File operations toolkit working.")
    print("Math operations toolkit working.")
    print("External package check completed.")
    print("Virtual environment information displayed.")

    print("\nUtility Toolkit is ready to use.")
    print("You can now import file_utils and math_utils in your projects.")


if __name__ == "__main__":
    main()
