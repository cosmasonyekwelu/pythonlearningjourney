"""
Math Utilities Module
=====================

A reusable collection of mathematical tools and operations designed
for quick calculations, statistical analysis, and geometry tasks.

Includes:
- Statistical computations (mean, median, standard deviation)
- Number utilities (factorial, prime check, Fibonacci sequence)
- Geometry helpers (circle area, circumference)
- Temperature conversions and random stats generation
"""

import math
import random
from typing import List, Tuple, Union, Optional, Dict

# --- Mathematical Constants ---
GOLDEN_RATIO = (1 + math.sqrt(5)) / 2
EULERS_NUMBER = math.e


# --- Basic Statistical Functions ---
def calculate_average(numbers: List[Union[int, float]]) -> Optional[float]:
    """
    Compute the arithmetic mean of a list of numbers.
    Returns None if the list is empty.
    """
    return sum(numbers) / len(numbers) if numbers else None


def calculate_median(numbers: List[Union[int, float]]) -> Optional[float]:
    """
    Compute the median value of a list of numbers.
    Returns None if the list is empty.
    """
    if not numbers:
        return None

    sorted_nums = sorted(numbers)
    n = len(sorted_nums)
    mid = n // 2
    return (sorted_nums[mid - 1] + sorted_nums[mid]) / 2 if n % 2 == 0 else sorted_nums[mid]


def calculate_standard_deviation(numbers: List[Union[int, float]]) -> Optional[float]:
    """
    Calculate the sample standard deviation for a list of numbers.
    Returns None if fewer than two values are provided.
    """
    if not numbers or len(numbers) < 2:
        return None
    mean = calculate_average(numbers)
    variance = sum((x - mean) ** 2 for x in numbers) / (len(numbers) - 1)
    return math.sqrt(variance)


# --- Number Utilities ---
def factorial(n: int) -> int:
    """
    Compute the factorial of a non-negative integer n.

    Raises:
        ValueError: If n is negative.
    """
    if n < 0:
        raise ValueError("Factorial is not defined for negative numbers.")
    return math.prod(range(1, n + 1)) if n > 1 else 1


def is_prime(n: int) -> bool:
    """
    Determine whether an integer n is a prime number.
    """
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(math.sqrt(n)) + 1, 2):
        if n % i == 0:
            return False
    return True


def fibonacci_sequence(n: int) -> List[int]:
    """
    Generate a Fibonacci sequence of n terms.
    Returns an empty list if n <= 0.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]
    if n == 2:
        return [0, 1]

    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq


# --- Geometry Helpers ---
def calculate_circle_area(radius: float) -> float:
    """Return the area of a circle with the given radius."""
    return math.pi * radius ** 2


def calculate_circle_circumference(radius: float) -> float:
    """Return the circumference of a circle with the given radius."""
    return 2 * math.pi * radius


# --- Algebra and Conversions ---
def solve_quadratic(a: float, b: float, c: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Solve a quadratic equation ax² + bx + c = 0.

    Returns:
        Tuple of two real roots (or None if no real roots exist).
    """
    discriminant = b ** 2 - 4 * a * c
    if discriminant < 0:
        return None, None
    elif discriminant == 0:
        return -b / (2 * a), None
    else:
        sqrt_d = math.sqrt(discriminant)
        return ((-b + sqrt_d) / (2 * a), (-b - sqrt_d) / (2 * a))


def convert_temperature(value: float, from_unit: str, to_unit: str) -> Optional[float]:
    """
    Convert temperature between Celsius (C), Fahrenheit (F), and Kelvin (K).
    """
    valid_units = {"C", "F", "K"}
    if from_unit not in valid_units or to_unit not in valid_units:
        return None

    # Convert source to Kelvin
    kelvin = (
        value + 273.15 if from_unit == "C"
        else (value - 32) * 5 / 9 + 273.15 if from_unit == "F"
        else value
    )

    # Convert Kelvin to target
    if to_unit == "C":
        return kelvin - 273.15
    elif to_unit == "F":
        return (kelvin - 273.15) * 9 / 5 + 32
    return kelvin


# --- Random and Statistical Demo Tools ---
def generate_random_stats(sample_size: int = 10) -> Dict[str, Union[List[float], float]]:
    """
    Generate random sample data and return basic descriptive statistics.
    """
    numbers = [random.uniform(1, 100) for _ in range(sample_size)]
    return {
        "numbers": numbers,
        "average": calculate_average(numbers),
        "median": calculate_median(numbers),
        "standard_deviation": calculate_standard_deviation(numbers),
        "min": min(numbers),
        "max": max(numbers),
    }


def display_math_constants() -> Dict[str, float]:
    """
    Return a dictionary of key mathematical constants and their values.
    """
    return {
        "π (Pi)": math.pi,
        "e (Euler’s Number)": EULERS_NUMBER,
        "φ (Golden Ratio)": GOLDEN_RATIO,
        "√2": math.sqrt(2),
        "√3": math.sqrt(3),
    }


# --- Demonstration Runner ---
if __name__ == "__main__":
    print("Math Utilities Demonstration\n")
    print(f"Fibonacci (10 terms): {fibonacci_sequence(10)}")
    print(f"Factorial of 5: {factorial(5)}")
    print(f"Is 17 prime? {'Yes' if is_prime(17) else 'No'}")
    print(f"25°C in Fahrenheit: {convert_temperature(25, 'C', 'F'):.2f}°F")
    print(f"Circle area (r=5): {calculate_circle_area(5):.2f}")
    print(f"Constants: {display_math_constants()}")
