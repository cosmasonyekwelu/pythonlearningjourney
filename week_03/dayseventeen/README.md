# Day 17: File I/O and Data Persistence

**Date:** October 8, 2025

## Learning Objective
To master reading from and writing to different file formats (Text, JSON, CSV) and understand how to persist data between program executions.

## Concepts Covered
- **Basic File I/O**: Opening, reading, writing, and appending to text files using context managers (`with` statement).
- **JSON Processing**: Serializing and deserializing Python objects using the `json` module.
- **CSV Handling**: Working with structured tabular data using `csv.reader`, `csv.writer`, and `DictReader/DictWriter`.
- **Configuration Files**: Using JSON to store and load application settings.
- **Data Persistence**: Building systems that save their state to the disk.

## Code Explanation
The `day_seventeen.py` script provides a toolkit for file operations:
- **FileOperations**: Demonstrates text file modes ('r', 'w', 'a') and how to handle `FileNotFoundError`.
- **JSON & CSV Demos**: Shows how to convert complex dictionaries to JSON and list data to CSV.
- **Contact Book Project**: A mini-project that implements a persistent address book. It saves contacts to a `contacts.json` file, allowing data to persist even after the script finishes.

## How to Run
Execute the script to see the file operations and the contact book demo:
```bash
python week_03/dayseventeen/day_seventeen.py
```

## Reflection
Data persistence is the key to creating useful applications. Mastering JSON for structured data and CSV for tabular data allows Python scripts to integrate with other tools and save progress across sessions.
