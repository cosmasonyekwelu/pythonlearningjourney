"""
Python Learning Journey - Day Fourteen
Week Two: Methods & Weekly Review Project
Date: October 5, 2025
Author: Cosmas Onyekwelu
"""


# Understanding Methods in OOP


class Student:
    school_name = "Univelcity Academy"

    def __init__(self, name, age, student_id):
        self.name = name
        self.age = age
        self.student_id = student_id
        self.courses = []

    # Instance method
    def enroll_course(self, course):
        self.courses.append(course)
        print(f"{self.name} enrolled in {course}")

    # Class method
    @classmethod
    def change_school(cls, new_name):
        cls.school_name = new_name
        print(f"School name changed to {cls.school_name}")

    # Static method
    @staticmethod
    def is_adult(age):
        return age >= 18


# Example usage of methods

student1 = Student("John Ajayi", 20, "STU001")
student2 = Student("Jane Okoko", 17, "STU002")

student1.enroll_course("Python Programming")
student2.enroll_course("Data Science")

print(Student.is_adult(student1.age))
print(Student.is_adult(student2.age))

Student.change_school("Univelcity Foxtrot Cohort")

print(student1.school_name)
print(student2.school_name)


# Weekly Review Project: Student Management System

class StudentManagementSystem:
    def __init__(self):
        self.students = {}

    def add_student(self, name, age, student_id):
        if student_id in self.students:
            print("Error: Student ID already exists.")
            return
        self.students[student_id] = Student(name, age, student_id)
        print(f"Student {name} added successfully.")

    def remove_student(self, student_id):
        if student_id not in self.students:
            print("Error: Student ID not found.")
            return
        removed = self.students.pop(student_id)
        print(f"Student {removed.name} removed successfully.")

    def list_students(self):
        if not self.students:
            print("No students in the system.")
            return
        for sid, student in self.students.items():
            print(
                f"{sid}: {student.name}, Age: {student.age}, Courses: {student.courses}")

    def enroll_student(self, student_id, course):
        if student_id not in self.students:
            print("Error: Student ID not found.")
            return
        self.students[student_id].enroll_course(course)


# Example usage
if __name__ == "__main__":
    system = StudentManagementSystem()
    system.add_student("Chris Brown", 22, "STU100")
    system.add_student("Michael Clinton", 19, "STU101")

    system.enroll_student("STU100", "Machine Learning")
    system.enroll_student("STU101", "Web Development")

    system.list_students()

    system.remove_student("STU101")
    system.list_students()
