# Day 17 - Python Learning Journey

**Date:** October 8, 2025

## Activities
- Mastered file operations using open() and context managers

- Practiced JSON serialization with json.load() and json.dump()

- Implemented CSV reading and writing using the csv module

- Learned configuration file handling for application settings

- Built a comprehensive Contact Book that persists data to JSON files

- Applied error handling for robust file operations

## Tutorial
Title: File I/O and Data Persistence

URL: Self-practice with Python file handling documentation

## Topics Covered:

- File operations with different modes (read, write, append)

- Context managers for safe file handling

- JSON serialization for structured data

- CSV module for tabular data

- Configuration files for application settings

- Error handling in file operations

## Key Learnings
- Understanding file modes and when to use each

- Mastering context managers for automatic resource cleanup

- Implementing JSON serialization for Python objects

- Working with CSV files for data exchange

- Creating configuration systems for applications

- Handling file-related exceptions gracefully

- Building data persistence layers for applications

## Code Examples
Basic File Operations
python
# Reading a file
with open('file.txt', 'r') as file:
    content = file.read()

# Writing to a file
with open('file.txt', 'w') as file:
    file.write('Hello, World!')
JSON Serialization
python
import json

# Writing to JSON
data = {'name': 'John', 'age': 30}
with open('data.json', 'w') as file:
    json.dump(data, file)

# Reading from JSON
with open('data.json', 'r') as file:
    data = json.load(file)
CSV Operations
python
import csv

# Writing CSV
with open('data.csv', 'w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['Name', 'Age'])
    writer.writerow(['John', 30])
## Practice Exercises
- Contact Book: Built a JSON-based contact management system

- Data Exporter: Created CSV export functionality for structured data

- Configuration Manager: Implemented settings persistence

- File Utilities: Developed reusable file handling functions

- Mini-Project: Contact Book System
## Features Implemented:

- Add, edit, delete, and search contacts

- JSON-based data persistence

- CSV export functionality

- Configuration management

- Comprehensive error handling

- Data validation and backup

## Reflection
Today's exploration of file I/O revealed the importance of data persistence in real-world applications. The context manager pattern proved essential for safe file handling, while JSON serialization provided a clean way to store complex data structures. CSV operations demonstrated practical data exchange capabilities, and configuration file handling showed how to make applications user-configurable. The Contact Book project successfully integrated all these concepts into a functional, persistent application.