# Day 06: Algorithms & File Handling

**Date:** September 27, 2025

## Learning Objective
To understand fundamental sorting and searching algorithms and master file I/O operations for text and CSV data.

## Concepts Covered
- **Sorting Algorithms**: Bubble Sort and Selection Sort (O(n²) complexity).
- **Searching Algorithms**: Linear Search (O(n)) and Binary Search (O(log n)).
- **Performance Benchmarking**: Comparing algorithm speed.
- **File Handling**: Reading and writing text files (`.txt`).
- **CSV Processing**: Reading and writing structured data using the `csv` module.
- **Big-O Notation**: Introduction to algorithmic complexity analysis.

## Code Explanation
The `day_six.py` script is organized into three classes:
- **AlgorithmMastery**: Implements classic algorithms. Note that while Bubble Sort is educational, Python's built-in `sorted()` is much more efficient.
- **FileHandling**: Contains methods for:
    - `read_text_file`: Reads an entire file.
    - `count_word_frequency`: Analyzes text files.
    - `read_csv_file` / `write_csv_file`: Manages structured data using `DictReader` and `DictWriter`.
- **ProblemSolvingExercises**: Orchestrates the demonstrations and provides a "Big-O" summary.

## How to Run
Run the script to see algorithms in action and file operations:
```bash
python week_01/daysix/day_six.py
```
This will also generate `sample.txt` and `contacts.csv` in the same directory.

## Reflection
Binary search is incredibly fast compared to linear search as the dataset grows. Learning to handle CSV files is essential for data science and automation tasks.
