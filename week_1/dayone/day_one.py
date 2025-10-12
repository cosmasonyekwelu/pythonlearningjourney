"""
Python Learning Journey - Day One
Date: September 22, 2025
Author: Cosmas Onyekwelu
Beginning my programming journey with Python fundamentals
"""

# Day One Learning Summary
day_one = {
    "date": "September 22, 2025",
    "activities": [
        "Attended orientation at Univelcity",
        "Completed 2-hour YouTube Python tutorial"
    ],
    "tutorial_details": {
        "title": "Python Tutorial - Full Course for Beginners",
        "url": "https://www.youtube.com/watch?v=K5KVEU3aaeQ&t=14s",
        "duration": "2 hours",
        "topics_covered": [
            "Python basics and syntax",
            "Variables and data types",
            "Basic operations and calculations",
            "Working with strings and lists"
        ]
    },
    "key_learnings": [
        "Python installation and environment setup",
        "Basic print statements and output",
        "Variable declaration and naming conventions",
        "Understanding different data types",
        "Simple arithmetic operations",
        "Basic string manipulation"
    ],
    "reflection": """
        Today marked the beginning of my Python programming journey. The orientation 
        at Univelcity provided a clear roadmap for what lies ahead, and the beginner 
        tutorial gave me solid foundational knowledge. I was able to set up my 
        development environment and write my first Python programs. I'm excited to 
        continue learning and building my programming skills day by day.
    """
}


def display_day_summary(day_data):
    """Display a formatted summary of the learning day"""
    print("=" * 60)
    print("PYTHON LEARNING JOURNEY - DAY ONE SUMMARY")
    print("=" * 60)

    print(f"Date: {day_data['date']}")

    print("\nToday's Activities:")
    for activity in day_data['activities']:
        print(f"  - {activity}")

    print("\nTutorial Completed:")
    tutorial = day_data['tutorial_details']
    print(f"  Title: {tutorial['title']}")
    print(f"  Duration: {tutorial['duration']}")
    print(f"  URL: {tutorial['url']}")
    print("  Topics Covered:")
    for topic in tutorial['topics_covered']:
        print(f"    * {topic}")

    print("\nKey Concepts Learned:")
    for learning in day_data['key_learnings']:
        print(f"  - {learning}")

    print(f"\nDaily Reflection:")
    print(f"  {day_data['reflection']}")


def practice_python_basics():
    """Practice the fundamental Python concepts learned today"""
    print("\n" + "=" * 40)
    print("PRACTICE: PYTHON FUNDAMENTALS")
    print("=" * 40)

    # Variables and basic data types
    print("\n--- Variables and Data Types ---")
    student_name = "Python Learner"
    student_age = 25
    student_height = 5.9
    is_beginner = True

    print(f"Student Name: {student_name}")
    print(f"Age: {student_age}")
    print(f"Height: {student_height}")
    print(f"Beginner Status: {is_beginner}")

    # Exploring different data types
    print("\n--- Exploring Data Types ---")
    examples = [
        ("Integer", 42, type(42)),
        ("Float", 3.14, type(3.14)),
        ("String", "Hello Python", type("Hello Python")),
        ("Boolean", False, type(False)),
        ("List", [1, 2, 3, 4, 5], type([1, 2, 3, 4, 5]))
    ]

    for data_type, value, type_info in examples:
        print(f"  {data_type}: {value} (Type: {type_info})")

    # Basic mathematical operations
    print("\n--- Basic Mathematical Operations ---")
    number_a = 15
    number_b = 4

    operations = [
        ("Addition", f"{number_a} + {number_b}", number_a + number_b),
        ("Subtraction", f"{number_a} - {number_b}", number_a - number_b),
        ("Multiplication", f"{number_a} * {number_b}", number_a * number_b),
        ("Division", f"{number_a} / {number_b}", number_a / number_b),
        ("Floor Division", f"{number_a} // {number_b}", number_a // number_b),
        ("Modulus", f"{number_a} % {number_b}", number_a % number_b)
    ]

    for operation_name, expression, result in operations:
        print(f"  {operation_name}: {expression} = {result}")

    # String operations practice
    print("\n--- Working with Strings ---")
    first_name = "Alice"
    last_name = "Smith"

    full_name = first_name + " " + last_name
    print(f"Full Name: {full_name}")
    print(f"Uppercase: {full_name.upper()}")
    print(f"Lowercase: {full_name.lower()}")
    print(f"Title Case: {full_name.title()}")
    print(f"Name Length: {len(full_name)} characters")
    print(f"First Name appears at position: {full_name.find(first_name)}")

    # Type conversion examples
    print("\n--- Type Conversion Examples ---")
    string_number = "123"
    converted_integer = int(string_number)
    print(
        f"String '{string_number}' converted to integer: {converted_integer}")

    decimal_string = "45.67"
    converted_float = float(decimal_string)
    print(f"String '{decimal_string}' converted to float: {converted_float}")

    number_to_string = str(789)
    print(f"Integer 789 converted to string: '{number_to_string}'")


def main():
    """Main function to run all Day One content"""
    # Display the day's learning summary
    display_day_summary(day_one)

    # Practice the concepts learned
    practice_python_basics()

    # Closing message
    print("\n" + "=" * 60)
    print("DAY ONE COMPLETED SUCCESSFULLY!")
    print("Looking forward to continuing this learning journey tomorrow.")
    print("=" * 60)


if __name__ == "__main__":
    main()
