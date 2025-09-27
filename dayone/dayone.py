"""
Python Learning Journey - Day One
Date: September 22, 2025
Author: Cosmas Onyekwelu
"""

# Day One Summary.
day_one = {
    "date": "September 22, 2025",
    "activities": [
        "Attended orientation at Univelcity",
        "Completed 2-hour YouTube Python tutorial"
    ],
    "tutorial_details": {
        "title": "Python Tutorial",
        "url": "https://www.youtube.com/watch?v=K5KVEU3aaeQ&t=14s",
        "duration": "2 hours",
        "topics_covered": [
            "Python basics",
            "Syntax fundamentals",
            "Variables and data types",
            "Basic operations"
        ]
    },
    "key_learnings": [
        "Python installation and setup",
        "Basic print statements",
        "Variable declaration and usage",
        "Understanding different data types",
        "Simple arithmetic operations"
    ],
    "reflection": """
        Today marked the beginning of my Python journey. The orientation at Univelcity 
        provided a good overview of what to expect, and the tutorial gave me solid 
        foundational knowledge. I'm excited to continue learning and building my 
        programming skills.
    """
}

# Display Day One Summary


def display_day_summary(day_data):
    """Display a formatted summary of the learning day"""
    print("=" * 50)
    print(f"PYTHON LEARNING JOURNEY - DAY ONE")
    print("=" * 50)
    print(f"Date: {day_data['date']}")
    print("\nActivities:")
    for i, activity in enumerate(day_data['activities'], 1):
        print(f"  {i}. {activity}")

    print(f"\nTutorial Details:")
    print(f"  Title: {day_data['tutorial_details']['title']}")
    print(f"  URL: {day_data['tutorial_details']['url']}")
    print(f"  Duration: {day_data['tutorial_details']['duration']}")
    print("  Topics Covered:")
    for topic in day_data['tutorial_details']['topics_covered']:
        print(f"    - {topic}")

    print("\nKey Learnings:")
    for i, learning in enumerate(day_data['key_learnings'], 1):
        print(f"  {i}. {learning}")

    print(f"\nReflection: {day_data['reflection']}")

# Basic Python Examples


def basic_python_examples():
    """Demonstrate basic Python concepts learned"""
    print("\n" + "="*30)
    print("CODE EXAMPLES FROM TODAY")
    print("="*30)


# Variables and data types
name = "Python Learner"
age = 25
height = 5.9
is_beginner = True

print(f"Name: {name}")
print(f"Age: {age}")
print(f"Height: {height}")
print(f"Beginner: {is_beginner}")

# Different data types
integer_var = 10
float_var = 3.14
string_var = "Hello Python"
boolean_var = True
list_var = [1, 2, 3, 4, 5]

print("Data Types Examples:")
print(f"Integer: {integer_var} - Type: {type(integer_var)}")
print(f"Float: {float_var} - Type: {type(float_var)}")
print(f"String: {string_var} - Type: {type(string_var)}")
print(f"Boolean: {boolean_var} - Type: {type(boolean_var)}")
print(f"List: {list_var} - Type: {type(list_var)}")

# Basic operations
a = 10
b = 3
print(f"\nBasic Operations:")
print(f"{a} + {b} = {a + b}")
print(f"{a} - {b} = {a - b}")
print(f"{a} * {b} = {a * b}")
print(f"{a} / {b} = {a / b:.2f}")

# STRING OPERATIONS
print("\n=== STRING OPERATIONS ===")
first_name = "Alice"
last_name = "Smith"

full_name = first_name + " " + last_name
print(f"Full Name: {full_name}")
print(f"Name in uppercase: {full_name.upper()}")
print(f"Name in lowercase: {full_name.lower()}")
print(f"Name length: {len(full_name)} characters")

#  TYPE CONVERSION
print("\n=== TYPE CONVERSION ===")
number_str = "123"
number_int = int(number_str)
print(f"String '123' converted to integer: {number_int}")

float_str = "45.67"
float_num = float(float_str)
print(f"String '45.67' converted to float: {float_num}")

#  USER INPUT
print("\n=== USER INPUT ===")
# Uncomment to try user input
# user_name = input("Enter your name: ")
# user_age = input("Enter your age: ")
# print(f"Hello {user_name}! You are {user_age} years old.")


# Main execution
if __name__ == "__main__":
    display_day_summary(day_one)
    basic_python_examples()
    print("\n" + "="*50)
    print("Keep coding! See you tomorrow!")
    print("="*50)
