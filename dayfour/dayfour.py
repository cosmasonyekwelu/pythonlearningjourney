"""
Python Learning Journey - Day One
Date: September 25, 2025
Author: Cosmas Onyekwelu
Topic: Control Flow Mastery & First Mini-Project
Building on Python basics with loops, conditionals, and interactive programming
"""

import random
from typing import List, Optional

# =============================================================================
# PART 1: CONTROL FLOW FUNDAMENTALS
# =============================================================================


def demonstrate_conditionals() -> None:
    """Demonstrate if/elif/else statements with practical examples"""
    print("=" * 50)
    print("PART 1: CONDITIONAL STATEMENTS")
    print("=" * 50)

    # Temperature classifier
    temperatures = [15, 25, -5, 32, 40, 10]
    print("\n🌡️  Temperature Classification:")
    for temp in temperatures:
        if temp < 0:
            category = "Freezing ❄️"
        elif temp < 15:
            category = "Cold 🥶"
        elif temp < 25:
            category = "Moderate 😊"
        elif temp < 35:
            category = "Warm ☀️"
        else:
            category = "Hot 🔥"
        print(f"   {temp}°C: {category}")


def demonstrate_loops() -> None:
    """Show for loops, while loops, and loop control statements"""
    print("\n" + "=" * 50)
    print("PART 2: LOOPS")
    print("=" * 50)

    # For loop with range
    print("\n🔢 Counting with for loop:")
    for i in range(1, 6):
        print(f"   Number {i}")

    # While loop with condition
    print("\n🔄 While loop countdown:")
    counter = 5
    while counter > 0:
        print(f"   T-minus {counter}...")
        counter -= 1
    print("   Liftoff! 🚀")

    # Break and continue examples
    print("\n⏹️  Break/Continue Demo:")
    print("   Numbers 1-10, skipping evens (continue):")
    for i in range(1, 11):
        if i % 2 == 0:
            continue
        print(f"   {i}", end=" ")

    print("\n\n   Stopping at 5 (break):")
    for i in range(1, 11):
        if i == 6:
            break
        print(f"   {i}", end=" ")
    print()


def demonstrate_nested_loops() -> None:
    """Show nested loops with practical examples"""
    print("\n" + "=" * 50)
    print("PART 3: NESTED LOOPS")
    print("=" * 50)

    # Multiplication table
    print("\n📊 Multiplication Table (1-3):")
    for i in range(1, 4):
        for j in range(1, 4):
            print(f"   {i} × {j} = {i*j}", end="  ")
        print()

    # Pattern printing
    print("\n🔺 Pattern Printing:")
    for row in range(1, 6):
        for col in range(1, row + 1):
            print("★", end=" ")
        print()

# =============================================================================
# PART 2: PRACTICAL EXERCISES
# =============================================================================


def fibonacci_sequence(count: int) -> List[int]:
    """Generate Fibonacci sequence using loops"""
    if count <= 0:
        return []
    elif count == 1:
        return [0]
    elif count == 2:
        return [0, 1]

    sequence = [0, 1]
    for i in range(2, count):
        next_num = sequence[i-1] + sequence[i-2]
        sequence.append(next_num)

    return sequence


def reverse_string(text: str) -> str:
    """Reverse a string using loop"""
    reversed_text = ""
    for i in range(len(text)-1, -1, -1):
        reversed_text += text[i]
    return reversed_text


def is_palindrome(text: str) -> bool:
    """Check if a string is palindrome using loop"""
    text = text.lower().replace(" ", "")
    for i in range(len(text) // 2):
        if text[i] != text[len(text)-1-i]:
            return False
    return True


def run_exercises() -> None:
    """Execute practical exercises"""
    print("\n" + "=" * 50)
    print("PART 4: PRACTICAL EXERCISES")
    print("=" * 50)

    # Fibonacci
    fib_numbers = fibonacci_sequence(10)
    print(f"\n🔢 First 10 Fibonacci numbers:")
    for i, num in enumerate(fib_numbers):
        print(f"   {i+1:2d}: {num:>3}")

    # String reversal
    test_strings = ["hello", "python", "racecar", "programming"]
    print(f"\n🔁 String Reversal:")
    for text in test_strings:
        reversed_text = reverse_string(text)
        palindrome_status = "✓" if is_palindrome(text) else "✗"
        print(f"   '{text}' → '{reversed_text}' {palindrome_status}")

# =============================================================================
# PART 3: INTERACTIVE MINI-PROJECT - NUMBER GUESSING GAME
# =============================================================================


class NumberGuessingGame:
    """Interactive number guessing game with scoring"""

    def __init__(self, min_num: int = 1, max_num: int = 50):
        self.min_num = min_num
        self.max_num = max_num
        self.target_number: Optional[int] = None
        self.attempts = 0
        self.high_score = None
        self.games_played = 0

    def generate_number(self) -> None:
        """Generate a new random number for the game"""
        self.target_number = random.randint(self.min_num, self.max_num)
        self.attempts = 0
        self.games_played += 1

    def get_user_guess(self) -> int:
        """Safely get and validate user input"""
        while True:
            try:
                guess = int(
                    input(f"   Enter guess ({self.min_num}-{self.max_num}): "))
                if self.min_num <= guess <= self.max_num:
                    return guess
                else:
                    print(
                        f"   ❌ Please enter between {self.min_num}-{self.max_num}")
            except ValueError:
                print("   ❌ Please enter a valid number!")

    def play_round(self) -> bool:
        """Play one round of guessing"""
        print(
            f"\n🎯 Game #{self.games_played}: I'm thinking of a number between {self.min_num}-{self.max_num}")

        while True:
            guess = self.get_user_guess()
            self.attempts += 1

            if guess == self.target_number:
                print(
                    f"   🎉 Correct! You guessed it in {self.attempts} attempts!")
                self._update_high_score()
                return True
            elif guess < self.target_number:
                print("   📈 Too low!", end=" ")
            else:
                print("   📉 Too high!", end=" ")

            # Give progressive hints
            if self.attempts % 3 == 0:
                hint_range = max(5, (self.max_num - self.min_num) // 4)
                lower_bound = max(
                    self.min_num, self.target_number - hint_range)
                upper_bound = min(
                    self.max_num, self.target_number + hint_range)
                print(f"💡 Hint: It's between {lower_bound}-{upper_bound}")
            else:
                print()

    def _update_high_score(self) -> None:
        """Update high score if current game is better"""
        if self.high_score is None or self.attempts < self.high_score:
            self.high_score = self.attempts
            print("   🏆 New high score!")

    def show_stats(self) -> None:
        """Display game statistics"""
        print(f"\n📊 Game Statistics:")
        print(f"   Games played: {self.games_played}")
        if self.high_score:
            print(f"   Best score: {self.high_score} attempts")
        else:
            print(f"   Best score: No wins yet")

    def play_again(self) -> bool:
        """Ask user if they want to play another round"""
        while True:
            choice = input("\n   Play again? (y/n): ").lower().strip()
            if choice in ['y', 'yes']:
                return True
            elif choice in ['n', 'no']:
                return False
            else:
                print("   Please enter 'y' or 'n'")

    def run(self) -> None:
        """Main game loop"""
        print("=" * 50)
        print("🎮 WELCOME TO THE NUMBER GUESSING GAME!")
        print("=" * 50)

        while True:
            self.generate_number()
            self.play_round()
            self.show_stats()

            if not self.play_again():
                print("\n" + "=" * 50)
                print("Thanks for playing! 👋")
                print("=" * 50)
                break

# =============================================================================
# MAIN EXECUTION
# =============================================================================


def main() -> None:
    """Main function to run all Day 4 content"""
    print("=" * 60)
    print("DAY 4: CONTROL FLOW MASTERY & INTERACTIVE PROGRAMMING")
    print("=" * 60)

    # Run fundamentals demonstration
    demonstrate_conditionals()
    demonstrate_loops()
    demonstrate_nested_loops()

    # Run practical exercises
    run_exercises()

    # Start interactive game
    print("\n" + "=" * 60)
    print("READY FOR THE MAIN EVENT: NUMBER GUESSING GAME!")
    print("=" * 60)

    game = NumberGuessingGame(min_num=1, max_num=50)
    game.run()

    # Final summary
    print("\n" + "=" * 60)
    print("DAY 4 COMPLETED! 🎓")
    print("You've mastered:")
    print("  ✓ Conditional statements (if/elif/else)")
    print("  ✓ Loops (for/while) and control flow")
    print("  ✓ Nested loops and pattern printing")
    print("  ✓ Practical algorithms (Fibonacci, palindrome)")
    print("  ✓ Interactive programming with user input")
    print("  ✓ Building a complete mini-game!")
    print("=" * 60)


if __name__ == "__main__":
    main()
