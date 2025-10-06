# Day 15 - Python Learning Journey

**Date:** October 6, 2025

---

## Activities

- Mastered inheritance concepts: single and multiple inheritance
- Practiced method overriding and `super()` function usage
- Implemented polymorphism with flexible method implementations
- Explored Method Resolution Order (MRO) in multiple inheritance
- Built a comprehensive **Vehicle class hierarchy** with `Car`, `Motorcycle`, and `Truck` subclasses
- Applied inheritance and polymorphism to create flexible, extensible code

---

## Tutorial

**Title:** Advanced OOP: Inheritance and Polymorphism  
**URL:** Self-practice with Python OOP documentation

---

## Topics Covered

- Single inheritance and class hierarchies
- Multiple inheritance and its complexities
- Method overriding for specialized behavior
- `super()` function for parent class access
- Polymorphism in practice
- Method Resolution Order (MRO)

---

## Key Learnings

- Understanding how inheritance enables code reuse and hierarchy creation
- Mastering method overriding to provide specialized implementations
- Using `super()` to access and extend parent class functionality
- Implementing polymorphism for flexible, interchangeable objects
- Navigating multiple inheritance with MRO understanding
- Designing class hierarchies that model real-world relationships

---

## Code Examples

### Basic Inheritance

```python
class Animal:
    def speak(self):
        pass

class Dog(Animal):
    def speak(self):
        return "Woof!"

class Cat(Animal):
    def speak(self):
        return "Meow"
```

---

### Method Overriding with `super()`

```python
class Vehicle:
    def __init__(self, make, model):
        self.make = make
        self.model = model

    def start_engine(self):
        return "Engine started"

class Car(Vehicle):
    def __init__(self, make, model, doors):
        super().__init__(make, model)
        self.doors = doors

    def start_engine(self):
        base_result = super().start_engine()
        return f"{base_result} - Car ready"
```

---

### Polymorphism in Action

```python
def make_animal_speak(animal):
    return animal.speak()

# Works with any Animal subclass
dog = Dog()
cat = Cat()
print(make_animal_speak(dog))  # "Woof!"
print(make_animal_speak(cat))  # "Meow"
```

---

## Practice Exercises

- **Animal Hierarchy:** Implement inheritance with `Animal` base class and multiple subclasses
- **Vehicle System:** Build a comprehensive vehicle hierarchy with specialized behaviors
- **Multiple Inheritance:** Create classes with multiple parents and explore MRO
- **Polymorphism Demo:** Build functions that work with any subclass object

---

## Mini-Project: Vehicle Management System

### Features Implemented

- Complete vehicle hierarchy with inheritance
- Method overriding for specialized vehicle behaviors
- Polymorphic functions that work with any vehicle type
- Multiple inheritance examples with hybrid vehicles
- MRO exploration and understanding

---

## Reflection

Today's deep dive into **inheritance** and **polymorphism** revealed the true power of object-oriented programming for creating flexible, maintainable code.
The `Animal` class example demonstrated how polymorphism allows writing generic code that works with any subclass.
The `Vehicle` hierarchy showed practical inheritance usage with method overriding and `super()` calls.
Understanding MRO helped navigate the complexities of multiple inheritance.
These concepts transform how we think about code organization, structure, and reusability.

```

```
