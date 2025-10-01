"""
Day 10: Advanced Lists & List Comprehensions
Python Learning Journey - Comprehensive List Operations
"""


class ListOperations:
    """Comprehensive list methods and operations"""

    def demonstrate_list_methods(self):
        """All essential list methods with examples"""
        print("=" * 60)
        print("List Methods Demonstration")
        print("=" * 60)

        # Initialize a sample list
        numbers = [1, 2, 3, 4, 5]
        print(f"Initial list: {numbers}")

        # Append method
        numbers.append(6)
        print(f"After append(6): {numbers}")

        # Extend method
        numbers.extend([7, 8])
        print(f"After extend([7, 8]): {numbers}")

        # Insert method
        numbers.insert(0, 0)
        print(f"After insert(0, 0): {numbers}")

        # Remove method
        numbers.remove(3)
        print(f"After remove(3): {numbers}")

        # Pop method
        popped = numbers.pop()
        print(f"After pop(): {numbers} (removed {popped})")

        popped_index = numbers.pop(2)
        print(f"After pop(2): {numbers} (removed {popped_index})")

        # Index method
        index_of_4 = numbers.index(4)
        print(f"Index of 4: {index_of_4}")

        # Count method
        numbers.append(2)
        count_of_2 = numbers.count(2)
        print(f"Count of 2: {count_of_2}")
        print(f"Current list: {numbers}")

        # Sort method
        numbers.sort()
        print(f"After sort(): {numbers}")

        numbers.sort(reverse=True)
        print(f"After sort(reverse=True): {numbers}")

        # Reverse method
        numbers.reverse()
        print(f"After reverse(): {numbers}")

        # Copy method
        numbers_copy = numbers.copy()
        print(f"Copy of list: {numbers_copy}")

        # Clear method
        numbers_copy.clear()
        print(f"After clear() on copy: {numbers_copy}")
        print(f"Original list unchanged: {numbers}")

    def demonstrate_list_slicing(self):
        """Advanced list slicing techniques"""
        print("\n" + "=" * 60)
        print("List Slicing Techniques")
        print("=" * 60)

        numbers = list(range(10))
        print(f"Original list: {numbers}")

        # Basic slicing
        print(f"numbers[2:6]: {numbers[2:6]}")
        print(f"numbers[:5]: {numbers[:5]}")
        print(f"numbers[5:]: {numbers[5:]}")

        # Negative indexing
        print(f"numbers[-3:]: {numbers[-3:]}")
        print(f"numbers[:-3]: {numbers[:-3]}")

        # Step slicing
        print(f"numbers[::2]: {numbers[::2]}")
        print(f"numbers[1::2]: {numbers[1::2]}")
        print(f"numbers[::-1]: {numbers[::-1]}")

        # Slice assignment
        numbers[2:5] = [20, 30, 40]
        print(f"After numbers[2:5] = [20, 30, 40]: {numbers}")

    def demonstrate_nested_lists(self):
        """Working with nested list structures"""
        print("\n" + "=" * 60)
        print("Nested Lists")
        print("=" * 60)

        # 2D list (matrix)
        matrix = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9]
        ]

        print("2D Matrix:")
        for row in matrix:
            print(f"  {row}")

        # Accessing elements
        print(f"matrix[0][1]: {matrix[0][1]}")
        print(f"matrix[2][0]: {matrix[2][0]}")

        # Modifying nested lists
        matrix[1][1] = 50
        print("After matrix[1][1] = 50:")
        for row in matrix:
            print(f"  {row}")

        # 3D list example
        cube = [
            [[1, 2], [3, 4]],
            [[5, 6], [7, 8]]
        ]
        print(f"3D list element cube[0][1][0]: {cube[0][1][0]}")


class ListComprehensions:
    """Advanced list comprehension techniques"""

    def demonstrate_basic_comprehensions(self):
        """Basic to intermediate list comprehensions"""
        print("\n" + "=" * 60)
        print("Basic List Comprehensions")
        print("=" * 60)

        # Simple comprehension
        squares = [x**2 for x in range(10)]
        print(f"Squares 0-9: {squares}")

        # Comprehension with condition
        even_squares = [x**2 for x in range(10) if x % 2 == 0]
        print(f"Even squares: {even_squares}")

        # Multiple conditions
        filtered = [x for x in range(20) if x % 2 == 0 if x % 3 == 0]
        print(f"Numbers divisible by 2 and 3: {filtered}")

        # If-else in comprehension
        categorized = ["even" if x % 2 == 0 else "odd" for x in range(10)]
        print(f"Even/odd categorization: {categorized}")

    def demonstrate_advanced_comprehensions(self):
        """Advanced list comprehension patterns"""
        print("\n" + "=" * 60)
        print("Advanced List Comprehensions")
        print("=" * 60)

        # Nested loops in comprehensions
        pairs = [(x, y) for x in range(3) for y in range(3)]
        print(f"All pairs 0-2: {pairs}")

        # Flattening 2D list
        matrix = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        flattened = [item for row in matrix for item in row]
        print(f"Flattened matrix: {flattened}")

        # Conditional nested comprehension
        filtered_pairs = [(x, y) for x in range(5) for y in range(5) if x != y]
        print(f"Pairs where x != y (first 10): {filtered_pairs[:10]}")

        # Dictionary comprehension from lists
        names = ['Alice', 'Bob', 'Charlie']
        name_lengths = {name: len(name) for name in names}
        print(f"Name lengths dictionary: {name_lengths}")

    def demonstrate_performance_comparison(self):
        """Compare comprehension vs traditional loops"""
        print("\n" + "=" * 60)
        print("Performance Comparison")
        print("=" * 60)

        import time

        # Large dataset
        data = list(range(10000))

        # Traditional loop approach
        start_time = time.time()
        result_loop = []
        for x in data:
            if x % 2 == 0:
                result_loop.append(x**2)
        loop_time = time.time() - start_time

        # List comprehension approach
        start_time = time.time()
        result_comp = [x**2 for x in data if x % 2 == 0]
        comp_time = time.time() - start_time

        print(f"Traditional loop time: {loop_time:.6f} seconds")
        print(f"List comprehension time: {comp_time:.6f} seconds")
        print(f"Comprehension is {loop_time/comp_time:.2f}x faster")
        print(f"Results equal: {result_loop == result_comp}")


class PracticeExercises:
    """Practice problems for lists and comprehensions"""

    def filter_even_numbers(self, numbers):
        """
        Filter even numbers using different approaches

        Args:
            numbers (list): List of integers

        Returns:
            tuple: (traditional_result, comprehension_result)
        """
        print(f"\nFiltering even numbers from: {numbers}")

        # Traditional approach
        traditional_result = []
        for num in numbers:
            if num % 2 == 0:
                traditional_result.append(num)

        # List comprehension approach
        comprehension_result = [num for num in numbers if num % 2 == 0]

        print(f"Traditional result: {traditional_result}")
        print(f"Comprehension result: {comprehension_result}")
        print(f"Results match: {traditional_result == comprehension_result}")

        return traditional_result, comprehension_result

    def flatten_2d_list(self, matrix):
        """
        Flatten a 2D list using different techniques

        Args:
            matrix (list): 2D list to flatten

        Returns:
            tuple: (traditional_result, comprehension_result)
        """
        print(f"\nFlattening 2D list: {matrix}")

        # Traditional nested loops
        traditional_result = []
        for row in matrix:
            for item in row:
                traditional_result.append(item)

        # List comprehension approach
        comprehension_result = [item for row in matrix for item in row]

        print(f"Traditional result: {traditional_result}")
        print(f"Comprehension result: {comprehension_result}")
        print(f"Results match: {traditional_result == comprehension_result}")

        return traditional_result, comprehension_result

    def process_student_grades(self):
        """Process student grades using list operations"""
        print("\n" + "=" * 50)
        print("Student Grades Processing")
        print("=" * 50)

        # Sample data: list of tuples (student, grades)
        student_grades = [
            ("Alice", [85, 92, 78]),
            ("Bob", [76, 88, 95]),
            ("Charlie", [92, 89, 84]),
            ("Diana", [79, 85, 88])
        ]

        # Calculate averages using list comprehension
        student_averages = [
            (student, sum(grades) / len(grades))
            for student, grades in student_grades
        ]

        print("Student averages:")
        for student, average in student_averages:
            print(f"  {student}: {average:.2f}")

        # Find students with average > 85
        high_achievers = [
            student for student, avg in student_averages
            if avg > 85
        ]
        print(f"High achievers (average > 85): {high_achievers}")

        # Get all grades flattened
        all_grades = [
            grade for student, grades in student_grades
            for grade in grades
        ]
        print(f"All grades: {all_grades}")
        print(f"Class average: {sum(all_grades) / len(all_grades):.2f}")

    def matrix_operations(self):
        """Perform various matrix operations using lists"""
        print("\n" + "=" * 50)
        print("Matrix Operations")
        print("=" * 50)

        matrix_a = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        matrix_b = [[9, 8, 7], [6, 5, 4], [3, 2, 1]]

        print("Matrix A:")
        for row in matrix_a:
            print(f"  {row}")

        print("Matrix B:")
        for row in matrix_b:
            print(f"  {row}")

        # Matrix transpose using comprehension
        transpose_a = [[row[i] for row in matrix_a]
                       for i in range(len(matrix_a[0]))]
        print("Transpose of A:")
        for row in transpose_a:
            print(f"  {row}")

        # Element-wise addition
        matrix_sum = [
            [matrix_a[i][j] + matrix_b[i][j] for j in range(len(matrix_a[0]))]
            for i in range(len(matrix_a))
        ]
        print("A + B (element-wise):")
        for row in matrix_sum:
            print(f"  {row}")


def main():
    """Main execution function"""
    print("DAY 10: ADVANCED LISTS & LIST COMPREHENSIONS")
    print("=" * 70)

    # Initialize classes
    list_ops = ListOperations()
    list_comps = ListComprehensions()
    exercises = PracticeExercises()

    # Demonstrate list operations
    list_ops.demonstrate_list_methods()
    list_ops.demonstrate_list_slicing()
    list_ops.demonstrate_nested_lists()

    # Demonstrate list comprehensions
    list_comps.demonstrate_basic_comprehensions()
    list_comps.demonstrate_advanced_comprehensions()
    list_comps.demonstrate_performance_comparison()

    # Practice exercises
    print("\n" + "=" * 70)
    print("PRACTICE EXERCISES")
    print("=" * 70)

    # Exercise 1: Filter even numbers
    numbers_list = list(range(15))
    exercises.filter_even_numbers(numbers_list)

    # Exercise 2: Flatten 2D list
    sample_matrix = [[1, 2, 3], [4, 5], [6, 7, 8, 9]]
    exercises.flatten_2d_list(sample_matrix)

    # Additional practical applications
    exercises.process_student_grades()
    exercises.matrix_operations()


if __name__ == "__main__":
    main()
