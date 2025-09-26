"""
Mini-Project: Student Gradebook System
"""

# Initialize gradebook
gradebook = {
    "Alice": [85, 90, 92],
    "Bob": [78, 81, 85],
    "Charlie": [95, 87, 93]
}


def add_student(name, grades):
    """Add a new student with their grades"""
    gradebook[name] = grades


def calculate_average(grades):
    """Return average of a list of grades"""
    return sum(grades) / len(grades)


def get_summary():
    """Print summary of all students"""
    print("\n=== Student Gradebook Summary ===")
    highest_score = 0
    lowest_score = 100
    top_student = ""
    bottom_student = ""

    for student, grades in gradebook.items():
        avg = calculate_average(grades)
        print(f"{student}: Grades={grades}, Average={avg:.2f}")

        if avg > highest_score:
            highest_score = avg
            top_student = student

        if avg < lowest_score:
            lowest_score = avg
            bottom_student = student

    print(f"\nTop Student: {top_student} with Avg {highest_score:.2f}")
    print(f"Lowest Student: {bottom_student} with Avg {lowest_score:.2f}")


# Example usage
add_student("Diana", [88, 90, 85])
get_summary()
