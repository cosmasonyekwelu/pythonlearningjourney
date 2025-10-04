"""
Day 13: Introduction to Object-Oriented Programming
Python Learning Journey - Classes, Objects, and OOP Fundamentals
"""


class OOPFundamentals:
    """Introduction to Object-Oriented Programming concepts"""
    
    def demonstrate_oop_concepts(self):
        """Explain OOP principles and benefits"""
        print("=" * 60)
        print("Object-Oriented Programming Fundamentals")
        print("=" * 60)
        
        print("What is OOP?")
        print("- A programming paradigm based on the concept of 'objects'")
        print("- Objects contain data (attributes) and code (methods)")
        print("- Models real-world entities and relationships")
        
        print("\nFour Pillars of OOP:")
        print("1. ENCAPSULATION: Bundling data and methods that work on that data")
        print("2. ABSTRACTION: Hiding complex implementation details")
        print("3. INHERITANCE: Creating new classes from existing ones")
        print("4. POLYMORPHISM: Using a unified interface for different data types")
        
        print("\nWhy use OOP?")
        print("- Modularity: Code organized into logical units")
        print("- Reusability: Classes can be reused across programs")
        print("- Maintainability: Easier to update and extend code")
        print("- Modeling: Naturally represents real-world scenarios")
    
    def demonstrate_class_definition(self):
        """Basic class definition and object creation"""
        print("\n" + "=" * 60)
        print("Class Definition and Object Creation")
        print("=" * 60)
        
        # Simple class example
        class Person:
            """A simple Person class representing a person with name and age"""
            
            def __init__(self, name, age):
                """Constructor method - initializes object attributes"""
                self.name = name
                self.age = age
                print(f"Created Person: {name}, {age} years old")
            
            def introduce(self):
                """Instance method - operates on object data"""
                return f"Hello, I'm {self.name} and I'm {self.age} years old"
            
            def have_birthday(self):
                """Method that modifies object state"""
                self.age += 1
                return f"Happy Birthday! {self.name} is now {self.age} years old"
        
        # Creating objects (instances) from the class
        print("Creating Person objects:")
        person1 = Person("Alice", 25)
        person2 = Person("Bob", 30)
        
        # Using object methods
        print("\nUsing object methods:")
        print(person1.introduce())
        print(person2.introduce())
        
        # Modifying object state
        print("\nModifying object state:")
        print(person1.have_birthday())
        print(person1.introduce())
        
        # Accessing object attributes
        print("\nAccessing attributes directly:")
        print(f"Person1 name: {person1.name}")
        print(f"Person1 age: {person1.age}")
        print(f"Person2 name: {person2.name}")
    
    def demonstrate_constructor_variations(self):
        """Different ways to use __init__ constructor"""
        print("\n" + "=" * 60)
        print("Constructor Variations")
        print("=" * 60)
        
        class Student:
            """Student class with different initialization patterns"""
            
            def __init__(self, name, student_id, major="Undeclared", gpa=0.0):
                """Constructor with default parameters"""
                self.name = name
                self.student_id = student_id
                self.major = major
                self.gpa = gpa
                self.courses = []  # Always initialized as empty list
            
            def enroll(self, course):
                """Add a course to student's schedule"""
                self.courses.append(course)
                return f"Enrolled in {course}"
            
            def update_gpa(self, new_gpa):
                """Update student's GPA with validation"""
                if 0.0 <= new_gpa <= 4.0:
                    self.gpa = new_gpa
                    return f"GPA updated to {new_gpa}"
                else:
                    return "Invalid GPA value"
            
            def get_info(self):
                """Return formatted student information"""
                return (f"Student: {self.name} (ID: {self.student_id})\n"
                       f"Major: {self.major}, GPA: {self.gpa}\n"
                       f"Courses: {', '.join(self.courses) if self.courses else 'None'}")
        
        # Creating students with different parameters
        student1 = Student("John Doe", "S12345")
        student2 = Student("Jane Smith", "S67890", "Computer Science", 3.8)
        student3 = Student("Bob Johnson", "S11111", "Mathematics")
        
        print("Student creations:")
        print(student1.get_info())
        print()
        print(student2.get_info())
        print()
        print(student3.get_info())
        
        # Using methods to modify state
        print("\nModifying student records:")
        student1.enroll("Python Programming")
        student1.enroll("Data Structures")
        student1.update_gpa(3.5)
        
        student3.enroll("Calculus")
        student3.update_gpa(3.2)
        
        print("\nUpdated student info:")
        print(student1.get_info())
        print()
        print(student3.get_info())
    
    def demonstrate_class_attributes(self):
        """Class vs instance attributes"""
        print("\n" + "=" * 60)
        print("Class Attributes vs Instance Attributes")
        print("=" * 60)
        
        class Bank:
            """Bank class demonstrating class-level attributes"""
            
            # Class attribute - shared by all instances
            bank_name = "Python National Bank"
            total_accounts = 0
            routing_number = "123456789"
            
            def __init__(self, account_holder, initial_balance=0):
                # Instance attributes - unique to each object
                self.account_holder = account_holder
                self.balance = initial_balance
                self.account_number = f"ACC{Bank.total_accounts + 1:06d}"
                
                # Update class attribute
                Bank.total_accounts += 1
                print(f"Created account {self.account_number} for {account_holder}")
            
            @classmethod
            def get_bank_info(cls):
                """Class method - operates on class-level data"""
                return (f"Bank: {cls.bank_name}\n"
                       f"Routing: {cls.routing_number}\n"
                       f"Total Accounts: {cls.total_accounts}")
            
            def get_account_info(self):
                """Instance method - operates on instance data"""
                return (f"Account: {self.account_number}\n"
                       f"Holder: {self.account_holder}\n"
                       f"Balance: ${self.balance:.2f}")
        
        # Using class attributes and methods
        print("Bank information (class level):")
        print(Bank.get_bank_info())
        
        # Creating instances
        print("\nCreating bank accounts:")
        account1 = Bank("Alice Johnson", 1000)
        account2 = Bank("Bob Smith", 500)
        
        print("\nUpdated bank information:")
        print(Bank.get_bank_info())
        
        print("\nAccount information (instance level):")
        print(account1.get_account_info())
        print()
        print(account2.get_account_info())
        
        # Demonstrating attribute access
        print("\nAttribute access examples:")
        print(f"Class attribute - bank_name: {Bank.bank_name}")
        print(f"Instance attribute - account1.balance: ${account1.balance}")


class PracticeExercises:
    """OOP practice exercises and mini-projects"""
    
    def create_student_class(self):
        """Student class practice exercise"""
        print("\n" + "=" * 50)
        print("Student Class Exercise")
        print("=" * 50)
        
        class Student:
            def __init__(self, name, student_id, major="Undeclared"):
                self.name = name
                self.student_id = student_id
                self.major = major
                self.grades = {}  # Dictionary to store course: grade
            
            def add_grade(self, course, grade):
                """Add a grade for a course"""
                if 0 <= grade <= 100:
                    self.grades[course] = grade
                    return f"Added grade {grade} for {course}"
                else:
                    return "Grade must be between 0 and 100"
            
            def calculate_gpa(self):
                """Calculate GPA from grades (4.0 scale)"""
                if not self.grades:
                    return 0.0
                
                total_points = 0
                for grade in self.grades.values():
                    if grade >= 90:
                        total_points += 4.0
                    elif grade >= 80:
                        total_points += 3.0
                    elif grade >= 70:
                        total_points += 2.0
                    elif grade >= 60:
                        total_points += 1.0
                    # Below 60 gets 0.0
                
                return total_points / len(self.grades)
            
            def get_transcript(self):
                """Generate a student transcript"""
                transcript = f"Transcript for {self.name}\n"
                transcript += f"Student ID: {self.student_id}\n"
                transcript += f"Major: {self.major}\n"
                transcript += f"GPA: {self.calculate_gpa():.2f}\n\n"
                transcript += "Courses and Grades:\n"
                
                for course, grade in self.grades.items():
                    transcript += f"  {course}: {grade}\n"
                
                return transcript
        
        # Test the Student class
        student = Student("Emily Chen", "S2024001", "Computer Science")
        
        print("Adding grades:")
        print(student.add_grade("Python Programming", 92))
        print(student.add_grade("Data Structures", 88))
        print(student.add_grade("Algorithms", 95))
        print(student.add_grade("Calculus", 76))
        
        print("\nStudent transcript:")
        print(student.get_transcript())
    
    def create_rectangle_class(self):
        """Rectangle class for geometric calculations"""
        print("\n" + "=" * 50)
        print("Rectangle Class Exercise")
        print("=" * 50)
        
        class Rectangle:
            def __init__(self, width, height):
                self.width = width
                self.height = height
            
            def area(self):
                """Calculate area of rectangle"""
                return self.width * self.height
            
            def perimeter(self):
                """Calculate perimeter of rectangle"""
                return 2 * (self.width + self.height)
            
            def is_square(self):
                """Check if rectangle is a square"""
                return self.width == self.height
            
            def scale(self, factor):
                """Scale rectangle dimensions by factor"""
                self.width *= factor
                self.height *= factor
                return f"Scaled to {self.width} x {self.height}"
            
            def get_info(self):
                """Return rectangle information"""
                shape_type = "Square" if self.is_square() else "Rectangle"
                return (f"{shape_type}: {self.width} x {self.height}\n"
                       f"Area: {self.area()}, Perimeter: {self.perimeter()}")
        
        # Test the Rectangle class
        rect1 = Rectangle(5, 10)
        rect2 = Rectangle(8, 8)  # Square
        
        print("Rectangle 1:")
        print(rect1.get_info())
        
        print("\nRectangle 2:")
        print(rect2.get_info())
        
        print(f"\nIs rect1 a square? {rect1.is_square()}")
        print(f"Is rect2 a square? {rect2.is_square()}")
        
        print("\nScaling rect1 by 2:")
        print(rect1.scale(2))
        print(rect1.get_info())
    
    def demonstrate_bank_account_concept(self):
        """Preview of BankAccount class concepts"""
        print("\n" + "=" * 50)
        print("Bank Account Concept Preview")
        print("=" * 50)
        
        class SimpleBankAccount:
            def __init__(self, account_holder, initial_balance=0):
                self.account_holder = account_holder
                self.balance = initial_balance
                self.transaction_history = []
                self._add_transaction("Account opened", initial_balance)
            
            def _add_transaction(self, description, amount):
                """Private method to record transactions"""
                self.transaction_history.append({
                    'description': description,
                    'amount': amount,
                    'balance': self.balance
                })
            
            def deposit(self, amount):
                """Deposit money into account"""
                if amount > 0:
                    self.balance += amount
                    self._add_transaction("Deposit", amount)
                    return f"Deposited ${amount:.2f}. New balance: ${self.balance:.2f}"
                else:
                    return "Deposit amount must be positive"
            
            def withdraw(self, amount):
                """Withdraw money from account"""
                if amount <= 0:
                    return "Withdrawal amount must be positive"
                elif amount > self.balance:
                    return "Insufficient funds"
                else:
                    self.balance -= amount
                    self._add_transaction("Withdrawal", -amount)
                    return f"Withdrew ${amount:.2f}. New balance: ${self.balance:.2f}"
            
            def get_balance(self):
                """Get current account balance"""
                return f"Balance: ${self.balance:.2f}"
            
            def get_statement(self):
                """Get account statement"""
                statement = f"Account Statement for {self.account_holder}\n"
                statement += f"Current Balance: ${self.balance:.2f}\n\n"
                statement += "Transaction History:\n"
                
                for transaction in self.transaction_history[-5:]:  # Last 5 transactions
                    statement += (f"  {transaction['description']}: "
                                 f"${transaction['amount']:.2f} | "
                                 f"Balance: ${transaction['balance']:.2f}\n")
                
                return statement
        
        # Test the simple bank account
        account = SimpleBankAccount("Alex Johnson", 1000)
        
        print("Initial account setup:")
        print(account.get_balance())
        
        print("\nPerforming transactions:")
        print(account.deposit(500))
        print(account.withdraw(200))
        print(account.withdraw(1500))  # Should fail
        print(account.deposit(100))
        
        print("\nAccount statement:")
        print(account.get_statement())


def main():
    """Main execution function"""
    print("DAY 13: INTRODUCTION TO OBJECT-ORIENTED PROGRAMMING")
    print("=" * 70)
    
    # Initialize classes
    oop_fundamentals = OOPFundamentals()
    practice_exercises = PracticeExercises()
    
    # Demonstrate OOP concepts
    oop_fundamentals.demonstrate_oop_concepts()
    oop_fundamentals.demonstrate_class_definition()
    oop_fundamentals.demonstrate_constructor_variations()
    oop_fundamentals.demonstrate_class_attributes()
    
    # Practice exercises
    print("\n" + "=" * 70)
    print("PRACTICE EXERCISES")
    print("=" * 70)
    
    practice_exercises.create_student_class()
    practice_exercises.create_rectangle_class()
    practice_exercises.demonstrate_bank_account_concept()
    
    print("\n" + "=" * 70)
    print("NEXT: Run bank_account.py for the complete BankAccount project!")
    print("=" * 70)


if __name__ == "__main__":
    main()