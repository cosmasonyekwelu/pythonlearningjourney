# Day 11: Advanced Dictionaries & Sets

**Date:** October 2, 2025

## Learning Objective
To master the usage of Dictionaries for mapped data and Sets for unique collections, focusing on efficiency and advanced comprehension techniques.

## Concepts Covered
- **Dictionary Methods**: Deep dive into `get`, `setdefault`, `update`, `popitem`, and dictionary views (`keys`, `values`, `items`).
- **Iteration Patterns**: Efficiently looping through dictionary components.
- **Dictionary Comprehensions**: Creating and transforming dictionaries using concise syntax.
- **Set Operations**: Union, intersection, difference, and symmetric difference using both methods and operators.
- **Set Membership**: Understanding the performance advantages of O(1) lookup in sets.
- **Data Deduplication**: Using sets to clean data and remove duplicates.

## Code Explanation
The `day_eleven.py` script explores:
- **DictionaryOperations**: Demonstrates how `setdefault` and `update` can simplify code.
- **SetOperations**: Uses mathematical operators (`|`, `&`, `-`, `^`) to perform set logic.
- **Set Membership Performance**: A benchmark showing that sets are orders of magnitude faster than lists for checking if an item exists.
- **PracticeExercises**: Includes:
    - `word_frequency_counter`: A robust counter that cleans punctuation.
    - `analyze_student_data`: Using set union to find all unique courses across multiple students.
    - `data_deduplication`: Practical examples of cleaning email lists and numeric data.

## How to Run
Execute the script to see the dictionary and set demonstrations:
```bash
python week_02/dayeleven/day_eleven.py
```

## Reflection
Dictionaries and sets are the backbone of efficient Python programs. The constant-time lookup for sets makes them the go-to choice for large-scale membership testing.
