# Day 14: OOP Methods & Student Management Project

**Date:** October 5, 2025

## Learning Objective
To master different types of methods in OOP (Instance, Class, and Static) and build a complete Student Management System.

## Concepts Covered
- **Instance Methods**: The most common type, accessing instance data via `self`.
- **Class Methods (`@classmethod`)**: Accessing class data via `cls`.
- **Static Methods (`@staticmethod`)**: Independent functions that don't need access to instance or class data.
- **Collection-based Management**: Using a dictionary to manage multiple objects.
- **Project Architecture**: Building a system that handles CRUD (Create, Read, Update, Delete) operations on objects.

## Code Explanation
The `day_fourteen.py` script consists of two main parts:
1. **Method Types Demonstration**:
    - `Student.enroll_course()`: An instance method that updates a student's courses.
    - `Student.change_school()`: A class method that updates the school name for all students simultaneously.
    - `Student.is_adult()`: A static method that performs a utility calculation based on age.
2. **Student Management System**:
    - `add_student()`: Creates a new `Student` object and stores it in a dictionary.
    - `enroll_student()`: Finds an existing object and calls its methods.
    - `list_students()`: Iterates through the collection to display all records.
    - `remove_student()`: Deletes an object from the system.

## How to Run
Run the management system script:
```bash
python week_02/dayfourteen/day_fourteen.py
```

## Reflection
Understanding the difference between instance, class, and static methods is crucial for designing clean OOP systems. Building the management system showed how powerful it is to store objects in collections for structured data management.
