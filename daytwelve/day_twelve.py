# Day 12 - Functions, Scope & Errors

# Example: simple function
def greet(name):
    return f"Hello, {name}!"


print(greet("Cosmas"))

# Demonstrating scope
x = 10  # global variable


def scope_demo():
    x = 5  # local variable
    print("Inside function:", x)


scope_demo()
print("Outside function:", x)

# Exception handling basics
try:
    num = int("10")
    result = 10 / 0
except ZeroDivisionError:
    print("Error: Division by zero is not allowed.")
except ValueError:
    print("Error: Invalid number format.")
else:
    print("Division successful:", result)
finally:
    print("Execution completed.")

# Raising an exception manually


def withdraw(balance, amount):
    if amount > balance:
        raise ValueError("Insufficient balance!")
    return balance - amount


try:
    print(withdraw(100, 150))
except ValueError as e:
    print("Custom error:", e)

# Custom exception class


class NegativeNumberError(Exception):
    pass


def square_root(num):
    if num < 0:
        raise NegativeNumberError(
            "Cannot calculate square root of a negative number.")
    return num ** 0.5


try:
    print(square_root(-9))
except NegativeNumberError as e:
    print("Custom Exception:", e)
