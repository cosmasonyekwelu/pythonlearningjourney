"""
Day 6: Algorithms & File Handling
Python Learning Journey - Algorithm Fundamentals & File I/O
"""

import csv
import time
import random
from typing import List, Dict, Any


class AlgorithmMastery:
    """Sorting and searching algorithms implementation"""

    def bubble_sort(self, arr: List[int]) -> List[int]:
        """Implement bubble sort algorithm"""
        n = len(arr)
        # Make a copy to avoid modifying original
        sorted_arr = arr.copy()

        for i in range(n):
            # Last i elements are already in place
            for j in range(0, n-i-1):
                if sorted_arr[j] > sorted_arr[j+1]:
                    # Swap elements
                    sorted_arr[j], sorted_arr[j +
                                              1] = sorted_arr[j+1], sorted_arr[j]

        return sorted_arr

    def selection_sort(self, arr: List[int]) -> List[int]:
        """Implement selection sort algorithm"""
        n = len(arr)
        sorted_arr = arr.copy()

        for i in range(n):
            # Find the minimum element in remaining unsorted array
            min_idx = i
            for j in range(i+1, n):
                if sorted_arr[j] < sorted_arr[min_idx]:
                    min_idx = j

            # Swap the found minimum element with the first element
            sorted_arr[i], sorted_arr[min_idx] = sorted_arr[min_idx], sorted_arr[i]

        return sorted_arr

    def linear_search(self, arr: List[int], target: int) -> int:
        """Implement linear search - returns index or -1 if not found"""
        for i in range(len(arr)):
            if arr[i] == target:
                return i
        return -1

    def binary_search(self, arr: List[int], target: int) -> int:
        """Implement binary search (requires sorted array)"""
        low = 0
        high = len(arr) - 1

        while low <= high:
            mid = (low + high) // 2
            if arr[mid] == target:
                return mid
            elif arr[mid] < target:
                low = mid + 1
            else:
                high = mid - 1

        return -1

    def compare_search_algorithms(self, data: List[int], target: int):
        """Compare linear vs binary search performance"""
        print(f"\n🔍 Searching for {target} in list of {len(data)} elements")

        # Linear search
        start_time = time.time()
        linear_result = self.linear_search(data, target)
        linear_time = time.time() - start_time

        # Binary search (requires sorted data)
        sorted_data = sorted(data)
        start_time = time.time()
        binary_result = self.binary_search(sorted_data, target)
        binary_time = time.time() - start_time

        print(
            f"Linear Search: Index {linear_result}, Time: {linear_time:.6f}s")
        print(
            f"Binary Search: Index {binary_result}, Time: {binary_time:.6f}s")

        if binary_time > 0:  # Avoid division by zero
            speedup = linear_time / binary_time
            print(f"Binary search is {speedup:.1f}x faster!")


class FileHandling:
    """File I/O operations and CSV handling"""

    def read_text_file(self, filename: str) -> str:
        """Read entire text file content"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except FileNotFoundError:
            return f"Error: File '{filename}' not found"
        except Exception as e:
            return f"Error reading file: {e}"

    def read_lines(self, filename: str) -> List[str]:
        """Read file line by line"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                lines = file.readlines()
            return [line.strip() for line in lines]
        except FileNotFoundError:
            return []

    def write_to_file(self, filename: str, content: str, mode: str = 'w'):
        """Write content to file (write or append mode)"""
        try:
            with open(filename, mode, encoding='utf-8') as file:
                file.write(content)
            return f"Successfully written to {filename}"
        except Exception as e:
            return f"Error writing to file: {e}"

    def count_word_frequency(self, filename: str) -> Dict[str, int]:
        """Count word frequency in a text file"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                text = file.read().lower()

            # Remove punctuation and split into words
            words = text.split()
            word_count = {}

            for word in words:
                # Clean word from punctuation
                clean_word = ''.join(char for char in word if char.isalnum())
                if clean_word:
                    word_count[clean_word] = word_count.get(clean_word, 0) + 1

            return word_count
        except FileNotFoundError:
            return {}

    def read_csv_file(self, filename: str) -> List[Dict[str, str]]:
        """Read CSV file using csv.DictReader"""
        try:
            with open(filename, 'r', encoding='utf-8') as file:
                csv_reader = csv.DictReader(file)
                return list(csv_reader)
        except FileNotFoundError:
            return []

    def write_csv_file(self, filename: str, data: List[Dict[str, str]], fieldnames: List[str]):
        """Write data to CSV file using csv.DictWriter"""
        try:
            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            return True
        except Exception as e:
            print(f"Error writing CSV: {e}")
            return False


class ProblemSolvingExercises:
    """Day 6 problem-solving exercises"""

    def demonstrate_algorithms(self):
        """Demonstrate sorting and searching algorithms"""
        print("🎯 ALGORITHM DEMONSTRATION")
        print("=" * 50)

        # Sample data
        numbers = [64, 34, 25, 12, 22, 11, 90, 5]
        print(f"Original list: {numbers}")

        # Sorting algorithms
        algo = AlgorithmMastery()

        bubble_sorted = algo.bubble_sort(numbers)
        print(f"Bubble Sort:   {bubble_sorted}")

        selection_sorted = algo.selection_sort(numbers)
        print(f"Selection Sort: {selection_sorted}")

        python_sorted = sorted(numbers)
        print(f"Python sorted(): {python_sorted}")

        # Searching algorithms
        target = 22
        linear_index = algo.linear_search(numbers, target)
        binary_index = algo.binary_search(sorted(numbers), target)

        print(f"\n🔍 Search for {target}:")
        print(f"Linear Search index: {linear_index}")
        print(f"Binary Search index: {binary_index}")

        # Performance comparison with larger dataset
        large_data = [random.randint(1, 10000) for _ in range(1000)]
        algo.compare_search_algorithms(large_data, target)

    def demonstrate_file_operations(self):
        """Demonstrate file handling operations"""
        print("\n📁 FILE HANDLING DEMONSTRATION")
        print("=" * 50)

        file_handler = FileHandling()

        # Create a sample text file
        sample_content = """Hello World! This is a sample text file.
Python File Handling is powerful and easy to use.
We can read, write, and append to files.
This is line 4 of our sample file."""

        # Write to file
        result = file_handler.write_to_file('sample.txt', sample_content)
        print(f"📝 {result}")

        # Read entire file
        content = file_handler.read_text_file('sample.txt')
        print(f"📖 File content:\n{content}")

        # Read line by line
        lines = file_handler.read_lines('sample.txt')
        print(f"📄 Lines: {len(lines)} lines read")

        # Word frequency count
        word_freq = file_handler.count_word_frequency('sample.txt')
        print(f"📊 Top 5 words: {dict(list(word_freq.items())[:5])}")

        # CSV operations demonstration
        self.demo_csv_operations()

    def demo_csv_operations(self):
        """Demonstrate CSV file operations"""
        print("\n📊 CSV FILE OPERATIONS")
        print("-" * 30)

        file_handler = FileHandling()

        # Sample data for CSV
        contacts_data = [
            {'name': 'Alice Johnson', 'phone': '123-456-7890',
                'email': 'alice@email.com'},
            {'name': 'Bob Smith', 'phone': '234-567-8901', 'email': 'bob@email.com'},
            {'name': 'Charlie Brown', 'phone': '345-678-9012',
                'email': 'charlie@email.com'}
        ]

        # Write to CSV
        fieldnames = ['name', 'phone', 'email']
        file_handler.write_csv_file('contacts.csv', contacts_data, fieldnames)
        print("✅ Created contacts.csv")

        # Read from CSV
        contacts = file_handler.read_csv_file('contacts.csv')
        print(f"📋 CSV Contacts: {len(contacts)} records")
        for contact in contacts:
            print(f"  - {contact['name']}: {contact['phone']}")


def main():
    """Main execution function"""
    print("🚀 DAY 6: ALGORITHMS & FILE HANDLING")
    print("=" * 60)

    # Run algorithm demonstrations
    exercises = ProblemSolvingExercises()
    exercises.demonstrate_algorithms()
    exercises.demonstrate_file_operations()

    # Big-O notation introduction
    print("\n📈 BIG-O NOTATION INTRODUCTION")
    print("=" * 40)
    print("""
O(1)     - Constant time (direct access)
O(log n) - Logarithmic time (binary search)
O(n)     - Linear time (linear search)
O(n²)    - Quadratic time (bubble sort, selection sort)
O(2ⁿ)    - Exponential time (avoid if possible!)

Today's algorithms:
- Linear Search: O(n)
- Binary Search: O(log n) 
- Bubble Sort: O(n²)
- Selection Sort: O(n²)
    """)


if __name__ == "__main__":
    main()
