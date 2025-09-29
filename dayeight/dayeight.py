"""
Python Learning Journey - Day Eight
Date: September 29, 2025
Author: Cosmas Onyekwelu
Topic: Comprehensive String Operations & Advanced Strings & Variables Mastery
"""


class StringMastery:
    """Comprehensive string operations and manipulations"""

    def demonstrate_indexing_slicing(self):
        """Advanced string indexing and slicing techniques"""
        print("=" * 60)
        print("STRING INDEXING & SLICING")
        print("=" * 60)

        text = "Python Programming Journey"

        # Positive indexing
        print("Positive Indexing:")
        print(f"  text[0]: '{text[0]}'")      # First character
        print(f"  text[7]: '{text[7]}'")      # 'P' in Programming
        print(f"  text[12]: '{text[12]}'")    # 'm' in Programming

        # Negative indexing
        print("\nNegative Indexing:")
        print(f"  text[-1]: '{text[-1]}'")    # Last character
        print(f"  text[-3]: '{text[-3]}'")    # 'r' in Journey
        print(f"  text[-7]: '{text[-7]}'")    # 'y' in Journey

        # Slicing techniques
        print("\nSlicing Techniques:")
        print(f"  text[0:6]: '{text[0:6]}'")          # 'Python'
        print(f"  text[7:18]: '{text[7:18]}'")        # 'Programming'
        print(f"  text[:6]: '{text[:6]}'")            # 'Python' (0 to 6)
        print(f"  text[7:]: '{text[7:]}'")            # 'Programming Journey'
        print(f"  text[-7:]: '{text[-7:]}'")          # 'Journey'
        print(f"  text[::2]: '{text[::2]}'")          # Every 2nd character
        print(f"  text[::-1]: '{text[::-1]}'")        # Reverse string

    def demonstrate_string_methods(self):
        """Comprehensive string methods demonstration"""
        print("\n" + "=" * 60)
        print("STRING METHODS")
        print("=" * 60)

        sample_text = "   Python Programming is FUN!   "
        print(f"Original: '{sample_text}'")

        # Case methods
        print(f"\nCase Methods:")
        print(f"  upper(): '{sample_text.upper()}'")
        print(f"  lower(): '{sample_text.lower()}'")
        print(f"  title(): '{sample_text.title()}'")
        print(f"  capitalize(): '{sample_text.capitalize()}'")
        print(f"  swapcase(): '{sample_text.swapcase()}'")

        # Whitespace and cleaning methods
        print(f"\nCleaning Methods:")
        print(f"  strip(): '{sample_text.strip()}'")
        print(f"  lstrip(): '{sample_text.lstrip()}'")
        print(f"  rstrip(): '{sample_text.rstrip()}'")

        # Search and replace methods
        print(f"\nSearch & Replace:")
        print(f"  find('Programming'): {sample_text.find('Programming')}")
        print(f"  count('o'): {sample_text.count('o')}")
        print(
            f"  replace('FUN', 'AMAZING'): '{sample_text.replace('FUN', 'AMAZING')}'")
        print(f"  startswith('Python'): {sample_text.startswith('Python')}")
        print(f"  endswith('!'): {sample_text.endswith('!')}")

        # Validation methods
        test_string = "Python123"
        print(f"\nValidation Methods:")
        print(f"  'Python123'.isalnum(): {test_string.isalnum()}")
        print(f"  'Python'.isalpha(): {'Python'.isalpha()}")
        print(f"  '123'.isdigit(): {'123'.isdigit()}")
        print(f"  'hello'.islower(): {'hello'.islower()}")
        print(f"  'HELLO'.isupper(): {'HELLO'.isupper()}")

    def demonstrate_string_formatting(self):
        """Various string formatting techniques"""
        print("\n" + "=" * 60)
        print("STRING FORMATTING")
        print("=" * 60)

        name = "Cosmas"
        age = 25
        language = "Python"
        day = 8

        # f-strings (Python 3.6+)
        print("f-strings:")
        message1 = f"Hello {name}, welcome to Day {day} of {language}!"
        print(f"  {message1}")

        # .format() method
        print("\n.format() method:")
        message2 = "Hello {}, welcome to Day {} of {}!".format(
            name, day, language)
        print(f"  {message2}")

        # Formatting with numbers and precision
        price = 49.98765
        print(f"\nNumber Formatting:")
        print(f"  Price: ${price:.2f}")
        print(f"  Percentage: {0.2567:.1%}")

        # Multi-line f-strings
        bio = f"""
        User Profile:
        Name: {name}
        Age: {age}
        Learning: {language}
        Day: {day}
        """
        print(f"\nMulti-line String:")
        print(bio)

    def demonstrate_variables(self):
        """Python variables and naming conventions"""
        print("\n" + "=" * 60)
        print("VARIABLES & NAMING CONVENTIONS")
        print("=" * 60)

        # Good variable names (Pythonic)
        student_name = "Alice"
        total_score = 95
        is_passed = True
        course_list = ["Python", "Data Structures", "Algorithms"]

        # Multiple assignment
        x, y, z = 10, 20, 30
        name, age, city = "Bob", 30, "New York"

        print("Good Variable Names:")
        print(f"  student_name = {student_name}")
        print(f"  total_score = {total_score}")
        print(f"  is_passed = {is_passed}")
        print(f"  course_list = {course_list}")

        print(f"\nMultiple Assignment:")
        print(f"  x, y, z = {x}, {y}, {z}")
        print(f"  name, age, city = {name}, {age}, {city}")

        # Variable swapping
        a, b = 5, 10
        print(f"\nVariable Swapping:")
        print(f"  Before: a = {a}, b = {b}")
        a, b = b, a
        print(f"  After: a = {a}, b = {b}")


class StringAlgorithms:
    """Practical string algorithm implementations"""

    def is_palindrome(self, text):
        """
        Check if a string is palindrome (case-insensitive, ignores spaces)

        Args:
            text (str): Input string to check

        Returns:
            bool: True if palindrome, False otherwise
        """
        # Clean the text: lowercase and remove spaces
        cleaned_text = text.lower().replace(" ", "")
        return cleaned_text == cleaned_text[::-1]

    def count_vowels(self, text):
        """
        Count the number of vowels in a string

        Args:
            text (str): Input string

        Returns:
            int: Number of vowels
        """
        vowels = "aeiou"
        count = 0

        for char in text.lower():
            if char in vowels:
                count += 1

        return count

    def analyze_text(self, text):
        """
        Comprehensive text analysis

        Args:
            text (str): Input text to analyze

        Returns:
            dict: Analysis results
        """
        analysis = {
            'original_text': text,
            'length': len(text),
            'word_count': len(text.split()),
            'vowel_count': self.count_vowels(text),
            'is_palindrome': self.is_palindrome(text),
            'reversed_text': text[::-1],
            'uppercase': text.upper(),
            'lowercase': text.lower()
        }

        return analysis


def main():
    """Main execution function"""
    print("DAY 8: ADVANCED STRINGS & VARIABLES")
    print("=" * 70)

    # Initialize classes
    string_master = StringMastery()
    algorithms = StringAlgorithms()

    # Demonstrate all string concepts
    string_master.demonstrate_indexing_slicing()
    string_master.demonstrate_string_methods()
    string_master.demonstrate_string_formatting()
    string_master.demonstrate_variables()

    # Practice exercises
    print("\n" + "=" * 70)
    print("PRACTICE EXERCISES")
    print("=" * 70)

    # Test strings for exercises
    test_cases = [
        "racecar",
        "A man a plan a canal Panama",
        "Python Programming",
        "Hello World",
        "Madam",
        "Was it a car or a cat I saw"
    ]

    print("PALINDROME CHECKS:")
    for test in test_cases:
        result = algorithms.is_palindrome(test)
        status = "PALINDROME" if result else "Not palindrome"
        print(f"  '{test}' -> {status}")

    print("\nVOWEL COUNTING:")
    vowel_tests = ["Hello World", "Python Programming", "AEIOU", "Rhythm"]
    for test in vowel_tests:
        count = algorithms.count_vowels(test)
        print(f"  '{test}' -> {count} vowels")

    print("\n" + "=" * 70)
    print("COMPREHENSIVE TEXT ANALYSIS")
    print("=" * 70)

    sample_text = "Python Programming is Amazing!"
    analysis = algorithms.analyze_text(sample_text)

    for key, value in analysis.items():
        print(f"  {key.replace('_', ' ').title():<15}: {value}")


if __name__ == "__main__":
    main()
