"""
Python Learning Journey - Day five
Date: September 26, 2025
Author: Cosmas Onyekwelu
Topic: Data Structures in Action & Problem Solving.
"""

# --- Lists ---
print("=== LISTS ===")
fruits = ["apple", "banana", "cherry", "date"]
print(f"Original List: {fruits}")
print(f"First element: {fruits[0]}")
print(f"Slicing [1:3]: {fruits[1:3]}")
squares = [x**2 for x in range(5)]
print(f"Squares using list comprehension: {squares}")

# --- Tuples ---
print("\n=== TUPLES ===")
coordinates = (10, 20)
x, y = coordinates  # tuple unpacking
print(f"Coordinates: {coordinates}")
print(f"Unpacked -> x: {x}, y: {y}")

# --- Sets ---
print("\n=== SETS ===")
set_a = {1, 2, 3, 4}
set_b = {3, 4, 5, 6}
print(f"Union: {set_a | set_b}")
print(f"Intersection: {set_a & set_b}")
print(f"Difference: {set_a - set_b}")

# --- Dictionaries ---
print("\n=== DICTIONARIES ===")
student = {"name": "Alice", "age": 21, "course": "Python"}
print(f"Student: {student}")
print(f"Name: {student['name']}")
student["grade"] = "A"
print(f"Updated Student: {student}")

# --- Problem Solving ---
print("\n=== PROBLEM SOLVING ===")

# 1. Reverse a list without built-in functions
nums = [1, 2, 3, 4, 5]
reversed_nums = []
for i in range(len(nums) - 1, -1, -1):
    reversed_nums.append(nums[i])
print(f"Reversed List: {reversed_nums}")

# 2. Find most frequent word in a string
text = "apple banana apple cherry banana apple"
words = text.split()
frequency = {}
for word in words:
    frequency[word] = frequency.get(word, 0) + 1
most_frequent = max(frequency, key=frequency.get)
print(f"Most Frequent Word: {most_frequent}")

# 3. Merge two dictionaries
dict1 = {"a": 1, "b": 2}
dict2 = {"c": 3, "d": 4}
merged = {**dict1, **dict2}
print(f"Merged Dictionary: {merged}")

# 4. Remove duplicates from a list
dup_list = [1, 2, 2, 3, 4, 4, 5]
no_duplicates = list(set(dup_list))
print(f"List without Duplicates: {no_duplicates}")
