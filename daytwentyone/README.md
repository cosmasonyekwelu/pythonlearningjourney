# Day 21 — Personal Library Manager
**Date:** October 12, 2025
**Week 3:**  Review & Project Polish

## Project Overview
A comprehensive library management system demonstrating object-oriented programming principles, data persistence, and API integration. This project serves as a capstone for Week 3, incorporating all concepts learned into a polished, production-ready application.

## Features

### Core Functionality
- **Book Management**: Add, edit, and delete books with inheritance (Book -> EBook, PrintBook)
- **Search and Filter**: Advanced search using polymorphism across different book types
- **Borrowing System**: Track borrowing history with due dates and overdue detection
- **Data Persistence**: Automatic save/load using JSON files
- **Reporting**: Generate comprehensive statistics and analytics reports

### Advanced Features
- **Google Books API Integration**: Import book information automatically
- **ISBN Validation**: Basic ISBN format validation
- **Multiple Book Types**: Support for both ebooks and print books with specialized attributes
- **Comprehensive Error Handling**: Graceful error recovery and user-friendly messages


## Installation and Setup

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

2. **Run the application**:  

```
   python day_twenty_one.py
```
## Adding Books
- Manual Entry: Add books by providing details through the menu interface

- API Import: Search and import books using Google Books API

- Book Types: Choose between EBook (digital) and PrintBook (physical) with type-specific attributes

## Managing Library
- Search: Find books by title, author, genre, or ISBN

- Filter: Narrow down books by type, availability, genre, or author

- Borrow/Return: Track book lending with automatic due date calculation

- Statistics: View comprehensive library analytics and usage patterns

## Data Management
- Automatic Saving: All changes are automatically persisted to JSON files

- Backup: Data is stored in the data/ directory

- Reports: Generate text and JSON reports in the reports/ directory

### Technical Implementation
## Object-Oriented Design
- Inheritance: Base Book class with EBook and PrintBook subclasses

- Polymorphism: Unified interface for different book types

- Encapsulation: Proper data hiding with getter methods

- Factory Pattern: Book creation through factory function

## Data Persistence
- JSON-based storage for books and borrowing history

- Automatic serialization/deserialization of complex objects

- Error handling for data corruption scenarios

## API Integration
- Google Books API for book information retrieval

- ISBN-based searching and data enrichment

- Graceful fallback for API failures


## Key Features Implemented

1. **Complete OOP Structure**: Inheritance hierarchy with proper polymorphism
2. **Data Persistence**: Automatic JSON serialization/deserialization
3. **API Integration**: Google Books API for book data enrichment
4. **Comprehensive Error Handling**: Graceful recovery from various error scenarios
5. **User-Friendly Interface**: Clear menu system with input validation
6. **Reporting System**: Text and JSON reports with analytics
7. **Modular Architecture**: Clean separation of concerns

This completes Day 21 with a polished, production-ready library management system that demonstrates all the concepts learned throughout Week 3!
