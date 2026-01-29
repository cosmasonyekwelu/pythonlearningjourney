# Day 21: Weekly Project – Personal Library Manager

**Date:** October 12, 2025

## Learning Objective
To integrate all of the OOP, File I/O, Error Handling, and API concepts learned in Week 3 into a comprehensive real-world application.

## Concepts Covered
- **Complex Class Hierarchies**: Using base classes (`Book`) and specialized subclasses (`EBook`, `PrintBook`).
- **Data persistence**: Storing the entire library state in JSON files.
- **Third-Party API Integration**: Importing book data directly from the Google Books API.
- **Reporting**: Generating text and JSON reports of library statistics.
- **Modular Project Structure**: Separating logic into `book.py`, `library_manager.py`, and `api_utils.py`.

## Code Explanation
The `PersonalLibraryApp` is a complete management system:
- **`LibraryManager`**: Handles the core logic of adding, removing, searching, and filtering books. It also manages borrowing and returning functionality.
- **`GoogleBooksAPI`**: Uses the `requests` library to fetch book details by title or ISBN.
- **`Book` Classes**: Use encapsulation to protect book details and provide a polymorphic `get_details()` method.
- **Statistics**: Automatically calculates utilization rates, overdue status, and genre distribution.

## How to Run
1. Install dependencies: `pip install requests`
2. Run the main application:
```bash
python week_03/daytwentyone/day_twenty_one.py
```
3. Use the menu to add books manually or via the Google Books API.

## Reflection
This project was the culmination of three weeks of learning. It demonstrates how inheritance allows for different book formats, how encapsulation protects data integrity, and how external APIs can add massive value to a simple utility script.
