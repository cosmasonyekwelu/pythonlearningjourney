"""
Python Learning Journey - Day Eleven
Date: October 1, 2025
Author: Cosmas Onyekwelu
Topic: Advanced Dictionaries & Sets.
"""


class DictionaryOperations:
    """Comprehensive dictionary methods and operations"""

    def demonstrate_dictionary_methods(self):
        """All essential dictionary methods with examples"""
        print("=" * 60)
        print("Dictionary Methods Demonstration")
        print("=" * 60)

        # Initialize a sample dictionary
        student = {
            "name": "Alice Johnson",
            "age": 22,
            "major": "Computer Science",
            "gpa": 3.8,
            "courses": ["Python", "Data Structures", "Algorithms"]
        }

        print(f"Initial dictionary: {student}")

        # Access methods
        print(f"Keys: {list(student.keys())}")
        print(f"Values: {list(student.values())}")
        print(f"Items: {list(student.items())}")

        # Get method with default
        print(f"Get 'name': {student.get('name')}")
        print(
            f"Get 'email' with default: {student.get('email', 'Not provided')}")

        # Setdefault method
        phone = student.setdefault('phone', '555-1234')
        print(f"After setdefault('phone', '555-1234'): {student}")

        # Update method
        student.update({'age': 23, 'year': 'Senior'})
        print(f"After update: {student}")

        # Pop method
        removed_gpa = student.pop('gpa')
        print(f"After pop('gpa'): {student} (removed {removed_gpa})")

        # Popitem method
        last_key, last_value = student.popitem()
        print(f"After popitem(): {student} (removed {last_key}: {last_value})")

        # Copy method
        student_copy = student.copy()
        print(f"Copy of dictionary: {student_copy}")

        # Clear method
        student_copy.clear()
        print(f"After clear() on copy: {student_copy}")
        print(f"Original dictionary unchanged: {student}")

    def demonstrate_dictionary_iteration(self):
        """Various ways to iterate through dictionaries"""
        print("\n" + "=" * 60)
        print("Dictionary Iteration Techniques")
        print("=" * 60)

        inventory = {
            'apples': 50,
            'bananas': 25,
            'oranges': 30,
            'grapes': 45
        }

        print("Inventory dictionary:", inventory)

        # Iterate through keys
        print("\nIterating through keys:")
        for key in inventory:
            print(f"  Key: {key}")

        # Iterate through keys explicitly
        print("\nIterating through keys():")
        for key in inventory.keys():
            print(f"  Key: {key}")

        # Iterate through values
        print("\nIterating through values:")
        for value in inventory.values():
            print(f"  Value: {value}")

        # Iterate through key-value pairs
        print("\nIterating through items():")
        for key, value in inventory.items():
            print(f"  {key}: {value}")

        # Dictionary comprehension with iteration
        print("\nDictionary comprehension (double values):")
        doubled_inventory = {item: quantity *
                             2 for item, quantity in inventory.items()}
        print(f"  {doubled_inventory}")

    def demonstrate_dictionary_comprehensions(self):
        """Advanced dictionary comprehension techniques"""
        print("\n" + "=" * 60)
        print("Dictionary Comprehensions")
        print("=" * 60)

        # Basic dictionary comprehension
        squares = {x: x**2 for x in range(1, 6)}
        print(f"Squares dictionary: {squares}")

        # Comprehension with condition
        even_squares = {x: x**2 for x in range(10) if x % 2 == 0}
        print(f"Even squares: {even_squares}")

        # Transforming existing dictionary
        prices = {'apple': 1.2, 'banana': 0.8, 'orange': 1.5}
        discounted_prices = {fruit: price *
                             0.9 for fruit, price in prices.items()}
        print(f"Discounted prices: {discounted_prices}")

        # Creating dictionary from two lists
        names = ['Alice', 'Bob', 'Charlie']
        scores = [85, 92, 78]
        grade_dict = {name: score for name, score in zip(names, scores)}
        print(f"Grade dictionary: {grade_dict}")

        # Nested dictionary comprehension
        matrix = {i: {j: i * j for j in range(1, 4)} for i in range(1, 4)}
        print(f"Multiplication table: {matrix}")


class SetOperations:
    """Comprehensive set methods and operations"""

    def demonstrate_set_methods(self):
        """All essential set methods with examples"""
        print("\n" + "=" * 60)
        print("Set Methods Demonstration")
        print("=" * 60)

        # Initialize sample sets
        set_a = {1, 2, 3, 4, 5}
        set_b = {4, 5, 6, 7, 8}

        print(f"Set A: {set_a}")
        print(f"Set B: {set_b}")

        # Basic set operations
        union_set = set_a.union(set_b)
        print(f"Union: {union_set}")

        intersection_set = set_a.intersection(set_b)
        print(f"Intersection: {intersection_set}")

        difference_set = set_a.difference(set_b)
        print(f"Difference (A - B): {difference_set}")

        symmetric_diff = set_a.symmetric_difference(set_b)
        print(f"Symmetric Difference: {symmetric_diff}")

        # Set modification methods
        set_a.add(6)
        print(f"After add(6): {set_a}")

        set_a.remove(1)
        print(f"After remove(1): {set_a}")

        set_a.discard(10)  # No error if not present
        print(f"After discard(10): {set_a}")

        popped = set_a.pop()
        print(f"After pop(): {set_a} (removed {popped})")

        # Set comparison methods
        print(f"Is subset: {set_a.issubset(set_b)}")
        print(f"Is superset: {set_a.issuperset({4, 5})}")
        print(f"Is disjoint: {set_a.isdisjoint({9, 10})}")

    def demonstrate_set_operations(self):
        """Mathematical set operations with operators"""
        print("\n" + "=" * 60)
        print("Set Operations with Operators")
        print("=" * 60)

        set_x = {1, 2, 3, 4, 5}
        set_y = {4, 5, 6, 7, 8}

        print(f"Set X: {set_x}")
        print(f"Set Y: {set_y}")

        # Union with | operator
        union_op = set_x | set_y
        print(f"Union (X | Y): {union_op}")

        # Intersection with & operator
        intersection_op = set_x & set_y
        print(f"Intersection (X & Y): {intersection_op}")

        # Difference with - operator
        difference_op = set_x - set_y
        print(f"Difference (X - Y): {difference_op}")

        # Symmetric difference with ^ operator
        symmetric_op = set_x ^ set_y
        print(f"Symmetric Difference (X ^ Y): {symmetric_op}")

        # Set comprehensions
        even_squares_set = {x**2 for x in range(10) if x % 2 == 0}
        print(f"Even squares set: {even_squares_set}")

    def demonstrate_set_membership(self):
        """Set membership testing and performance"""
        print("\n" + "=" * 60)
        print("Set Membership Testing")
        print("=" * 60)

        import time

        # Large datasets for performance comparison
        large_list = list(range(100000))
        large_set = set(large_list)

        # Test membership in list vs set
        test_value = 99999

        # List membership test
        start_time = time.time()
        list_result = test_value in large_list
        list_time = time.time() - start_time

        # Set membership test
        start_time = time.time()
        set_result = test_value in large_set
        set_time = time.time() - start_time

        print(f"List membership test: {list_time:.6f} seconds")
        print(f"Set membership test: {set_time:.6f} seconds")
        print(
            f"Set is {list_time/set_time:.0f}x faster for membership testing")
        print(f"Results equal: {list_result == set_result}")


class PracticeExercises:
    """Practice problems for dictionaries and sets"""

    def word_frequency_counter(self, text):
        """
        Count frequency of each word in text using dictionary

        Args:
            text (str): Input text to analyze

        Returns:
            dict: Word frequency dictionary
        """
        print(f"\nWord Frequency Analysis for: '{text}'")

        # Convert to lowercase and split into words
        words = text.lower().split()
        frequency = {}

        # Count word frequency
        for word in words:
            # Remove punctuation
            clean_word = word.strip('.,!?;:"')
            if clean_word:
                frequency[clean_word] = frequency.get(clean_word, 0) + 1

        print("Word frequencies:")
        for word, count in frequency.items():
            print(f"  '{word}': {count}")

        return frequency

    def find_unique_values(self, data):
        """
        Find unique values in data using sets

        Args:
            data: List of values (can be any hashable type)

        Returns:
            set: Set of unique values
        """
        print(f"\nFinding unique values in: {data}")

        # Convert to set to get unique values
        unique_values = set(data)

        print(f"Total items: {len(data)}")
        print(f"Unique items: {len(unique_values)}")
        print(f"Unique values: {sorted(unique_values)}")

        return unique_values

    def analyze_student_data(self):
        """Analyze student data using dictionaries and sets"""
        print("\n" + "=" * 50)
        print("Student Data Analysis")
        print("=" * 50)

        # Sample student data
        students = [
            {"name": "Alice", "courses": {
                "Math", "Physics", "Chemistry"}, "grade": "A"},
            {"name": "Bob", "courses": {"Math", "Biology", "English"}, "grade": "B"},
            {"name": "Charlie", "courses": {
                "Physics", "Chemistry", "Art"}, "grade": "A"},
            {"name": "Diana", "courses": {
                "Math", "Physics", "Computer Science"}, "grade": "A"},
            {"name": "Eve", "courses": {"Biology", "English", "History"}, "grade": "C"}
        ]

        # Create dictionary mapping grades to students
        grade_dict = {}
        for student in students:
            grade = student["grade"]
            if grade not in grade_dict:
                grade_dict[grade] = []
            grade_dict[grade].append(student["name"])

        print("Students by grade:")
        for grade, names in grade_dict.items():
            print(f"  Grade {grade}: {names}")

        # Find all unique courses using set union
        all_courses = set()
        for student in students:
            all_courses |= student["courses"]  # Union operation

        print(f"All courses offered: {sorted(all_courses)}")

        # Find most popular course
        course_popularity = {}
        for student in students:
            for course in student["courses"]:
                course_popularity[course] = course_popularity.get(
                    course, 0) + 1

        most_popular = max(course_popularity, key=course_popularity.get)
        print(
            f"Most popular course: {most_popular} ({course_popularity[most_popular]} students)")

    def data_deduplication(self):
        """Demonstrate data deduplication using sets"""
        print("\n" + "=" * 50)
        print("Data Deduplication")
        print("=" * 50)

        # Sample data with duplicates
        duplicate_emails = [
            "user1@example.com", "user2@example.com", "user1@example.com",
            "user3@example.com", "user2@example.com", "user4@example.com",
            "user1@example.com", "user5@example.com"
        ]

        duplicate_numbers = [1, 2, 2, 3, 4, 4, 5, 1, 6, 7, 7, 8, 2, 9]

        print("Email list with duplicates:")
        print(f"  {duplicate_emails}")

        unique_emails = set(duplicate_emails)
        print(f"Unique emails: {sorted(unique_emails)}")
        print(
            f"Removed {len(duplicate_emails) - len(unique_emails)} duplicates")

        print(f"\nNumber list with duplicates: {duplicate_numbers}")
        unique_numbers = set(duplicate_numbers)
        print(f"Unique numbers: {sorted(unique_numbers)}")
        print(
            f"Removed {len(duplicate_numbers) - len(unique_numbers)} duplicates")

        # Demonstrate set operations for data cleaning
        valid_users = {"user1@example.com",
                       "user2@example.com", "user3@example.com"}
        current_users = set(duplicate_emails)

        unauthorized_users = current_users - valid_users
        authorized_users = current_users & valid_users

        print(f"\nValid users: {valid_users}")
        print(f"Unauthorized users: {unauthorized_users}")
        print(f"Authorized users: {authorized_users}")


def main():
    """Main execution function"""
    print("DAY 11: ADVANCED DICTIONARIES & SETS")
    print("=" * 70)

    # Initialize classes
    dict_ops = DictionaryOperations()
    set_ops = SetOperations()
    exercises = PracticeExercises()

    # Demonstrate dictionary operations
    dict_ops.demonstrate_dictionary_methods()
    dict_ops.demonstrate_dictionary_iteration()
    dict_ops.demonstrate_dictionary_comprehensions()

    # Demonstrate set operations
    set_ops.demonstrate_set_methods()
    set_ops.demonstrate_set_operations()
    set_ops.demonstrate_set_membership()

    # Practice exercises
    print("\n" + "=" * 70)
    print("PRACTICE EXERCISES")
    print("=" * 70)

    # Exercise 1: Word frequency counter
    sample_text = "Hello world hello python world data python hello"
    exercises.word_frequency_counter(sample_text)

    # Exercise 2: Unique values
    sample_data = [1, 2, 2, 3, 4, 4, 5, 1, 6, 7, 7, 8, 2, 9]
    exercises.find_unique_values(sample_data)

    # Additional practical applications
    exercises.analyze_student_data()
    exercises.data_deduplication()


if __name__ == "__main__":
    main()
