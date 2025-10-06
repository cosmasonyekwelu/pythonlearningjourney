"""
Python Learning Journey - Day Fifteen
Date: October 6, 2025
Author: Cosmas Onyekwelu
Topic: Advanced OOP: Inheritance and Polymorphism
"""


class InheritanceFundamentals:
    """Demonstration of inheritance concepts and patterns"""

    def demonstrate_single_inheritance(self):
        """Basic single inheritance with method overriding"""
        print("=" * 60)
        print("Single Inheritance")
        print("=" * 60)

        # Base class
        class Animal:
            def __init__(self, name, species):
                self.name = name
                self.species = species
                print(f"Created {self.species} named {self.name}")

            def speak(self):
                return "Some generic animal sound"

            def move(self):
                return f"{self.name} is moving"

            def get_info(self):
                return f"{self.name} the {self.species}"

        # Derived class - single inheritance
        class Dog(Animal):
            def __init__(self, name, breed):
                # Call parent class constructor
                super().__init__(name, "Dog")
                self.breed = breed

            # Method overriding - providing specialized implementation
            def speak(self):
                return "Woof!"

            def fetch(self):
                return f"{self.name} is fetching the ball"

            # Extended method with additional functionality
            def get_info(self):
                base_info = super().get_info()
                return f"{base_info} of breed {self.breed}"

        # Another derived class
        class Cat(Animal):
            def __init__(self, name, color):
                super().__init__(name, "Cat")
                self.color = color

            def speak(self):
                return "Meow"

            def climb(self):
                return f"{self.name} is climbing a tree"

            def get_info(self):
                return f"{super().get_info()} with {self.color} fur"

        # Demonstrate inheritance
        print("Creating animals:")
        generic_animal = Animal("Generic", "Unknown")
        dog = Dog("Buddy", "Golden Retriever")
        cat = Cat("Whiskers", "orange")

        print("\nMethod calls - demonstrating inheritance:")
        print(f"Generic animal: {generic_animal.speak()}")
        print(f"Dog: {dog.speak()}")
        print(f"Cat: {cat.speak()}")

        print(f"\nAnimal movement (inherited method):")
        print(f"Dog: {dog.move()}")
        print(f"Cat: {cat.move()}")

        print(f"\nSpecialized methods:")
        print(f"Dog: {dog.fetch()}")
        print(f"Cat: {cat.climb()}")

        print(f"\nExtended methods using super():")
        print(f"Dog info: {dog.get_info()}")
        print(f"Cat info: {cat.get_info()}")

        print(f"\nInheritance relationships:")
        print(f"Is Dog subclass of Animal? {issubclass(Dog, Animal)}")
        print(f"Is dog instance of Animal? {isinstance(dog, Animal)}")
        print(f"Is dog instance of Dog? {isinstance(dog, Dog)}")

    def demonstrate_multiple_inheritance(self):
        """Multiple inheritance and method resolution order"""
        print("\n" + "=" * 60)
        print("Multiple Inheritance")
        print("=" * 60)

        class Engine:
            def __init__(self, horsepower):
                self.horsepower = horsepower

            def start(self):
                return "Engine starting..."

            def get_engine_info(self):
                return f"Engine: {self.horsepower} HP"

        class ElectricSystem:
            def __init__(self, battery_capacity):
                self.battery_capacity = battery_capacity

            def charge(self):
                return "Charging electric system..."

            def get_electric_info(self):
                return f"Battery: {self.battery_capacity} kWh"

            # This method will be overridden in hybrid vehicle
            def get_power_info(self):
                return "Electric power system"

        class HybridVehicle(Engine, ElectricSystem):
            def __init__(self, horsepower, battery_capacity, model):
                # Initialize both parent classes
                Engine.__init__(self, horsepower)
                ElectricSystem.__init__(self, battery_capacity)
                self.model = model

            def start(self):
                engine_start = Engine.start(self)
                electric_ready = "Electric system ready"
                return f"{engine_start} {electric_ready} - Hybrid system operational"

            # Override method from ElectricSystem
            def get_power_info(self):
                engine_info = Engine.get_engine_info(self)
                electric_info = ElectricSystem.get_electric_info(self)
                return f"Hybrid System: {engine_info}, {electric_info}"

            def get_vehicle_info(self):
                return f"Hybrid Vehicle: {self.model}"

        # Demonstrate multiple inheritance
        print("Creating hybrid vehicle with multiple inheritance:")
        hybrid_car = HybridVehicle(150, 50, "EcoCar 2000")

        print(f"\nMethod calls from multiple parents:")
        print(f"Start: {hybrid_car.start()}")
        print(f"Charge: {hybrid_car.charge()}")
        print(f"Engine info: {hybrid_car.get_engine_info()}")
        print(f"Electric info: {hybrid_car.get_electric_info()}")

        print(f"\nOverridden method:")
        print(f"Power info: {hybrid_car.get_power_info()}")

        print(f"\nMethod Resolution Order (MRO):")
        print(HybridVehicle.__mro__)

        print(f"\nInheritance checks:")
        print(
            f"Is HybridVehicle subclass of Engine? {issubclass(HybridVehicle, Engine)}")
        print(
            f"Is HybridVehicle subclass of ElectricSystem? {issubclass(HybridVehicle, ElectricSystem)}")
        print(
            f"Is hybrid_car instance of Engine? {isinstance(hybrid_car, Engine)}")
        print(
            f"Is hybrid_car instance of ElectricSystem? {isinstance(hybrid_car, ElectricSystem)}")

    def demonstrate_polymorphism(self):
        """Polymorphism in practice - same interface, different implementations"""
        print("\n" + "=" * 60)
        print("Polymorphism")
        print("=" * 60)

        class Shape:
            def area(self):
                pass

            def perimeter(self):
                pass

            def describe(self):
                return "I am a shape"

        class Rectangle(Shape):
            def __init__(self, width, height):
                self.width = width
                self.height = height

            def area(self):
                return self.width * self.height

            def perimeter(self):
                return 2 * (self.width + self.height)

            def describe(self):
                return f"Rectangle {self.width}x{self.height}"

        class Circle(Shape):
            def __init__(self, radius):
                self.radius = radius

            def area(self):
                import math
                return math.pi * self.radius ** 2

            def perimeter(self):
                import math
                return 2 * math.pi * self.radius

            def describe(self):
                return f"Circle with radius {self.radius}"

        class Triangle(Shape):
            def __init__(self, base, height, side1, side2, side3):
                self.base = base
                self.height = height
                self.side1 = side1
                self.side2 = side2
                self.side3 = side3

            def area(self):
                return 0.5 * self.base * self.height

            def perimeter(self):
                return self.side1 + self.side2 + self.side3

            def describe(self):
                return f"Triangle with base {self.base}, height {self.height}"

        # Demonstrate polymorphism
        shapes = [
            Rectangle(5, 10),
            Circle(7),
            Triangle(6, 8, 5, 5, 6)
        ]

        print("Polymorphic behavior - same method names, different implementations:")
        for shape in shapes:
            print(f"\n{shape.describe()}:")
            print(f"  Area: {shape.area():.2f}")
            print(f"  Perimeter: {shape.perimeter():.2f}")

        # Polymorphic function
        def print_shape_statistics(shape_objects):
            print(f"\nShape Statistics:")
            total_area = sum(shape.area() for shape in shape_objects)
            total_perimeter = sum(shape.perimeter() for shape in shape_objects)

            print(f"Total area: {total_area:.2f}")
            print(f"Total perimeter: {total_perimeter:.2f}")
            print(f"Number of shapes: {len(shape_objects)}")

            for shape in shape_objects:
                print(f"  - {shape.describe()}: area={shape.area():.2f}")

        print_shape_statistics(shapes)

        # Another polymorphic example
        def describe_all(shapes_list):
            return [shape.describe() for shape in shapes_list]

        descriptions = describe_all(shapes)
        print(f"\nAll shape descriptions: {descriptions}")


class VehicleHierarchyProject:
    """Practice Project: Vehicle class hierarchy with inheritance and polymorphism"""

    def create_vehicle_hierarchy(self):
        """Comprehensive vehicle hierarchy with Car, Motorcycle, and Truck"""
        print("\n" + "=" * 60)
        print("Vehicle Hierarchy Project")
        print("=" * 60)

        # Base Vehicle class
        class Vehicle:
            def __init__(self, make, model, year, fuel_type):
                self.make = make
                self.model = model
                self.year = year
                self.fuel_type = fuel_type
                self._mileage = 0  # Protected attribute
                self._is_running = False

            def start_engine(self):
                if not self._is_running:
                    self._is_running = True
                    return f"{self.get_display_name()} engine started"
                return "Engine is already running"

            def stop_engine(self):
                if self._is_running:
                    self._is_running = False
                    return f"{self.get_display_name()} engine stopped"
                return "Engine is already stopped"

            def drive(self, distance):
                if self._is_running:
                    if distance > 0:
                        self._mileage += distance
                        return f"Drove {distance} miles. Total mileage: {self._mileage}"
                    return "Distance must be positive"
                return "Cannot drive - engine is not running"

            def get_display_name(self):
                return f"{self.year} {self.make} {self.model}"

            def get_vehicle_info(self):
                return (f"{self.get_display_name()} | "
                        f"Fuel: {self.fuel_type} | "
                        f"Mileage: {self._mileage} | "
                        f"Running: {self._is_running}")

            # Abstract method pattern (Python doesn't have true abstract methods without ABC)
            def get_vehicle_type(self):
                raise NotImplementedError(
                    "Subclasses must implement get_vehicle_type")

        # Car class - inherits from Vehicle
        class Car(Vehicle):
            def __init__(self, make, model, year, fuel_type, doors, passenger_capacity):
                super().__init__(make, model, year, fuel_type)
                self.doors = doors
                self.passenger_capacity = passenger_capacity
                self._trunk_open = False

            def open_trunk(self):
                if not self._trunk_open:
                    self._trunk_open = True
                    return "Trunk opened"
                return "Trunk is already open"

            def close_trunk(self):
                if self._trunk_open:
                    self._trunk_open = False
                    return "Trunk closed"
                return "Trunk is already closed"

            # Override parent method
            def start_engine(self):
                base_result = super().start_engine()
                if "started" in base_result:
                    return f"{base_result} - Car ready for {self.passenger_capacity} passengers"
                return base_result

            def get_vehicle_info(self):
                base_info = super().get_vehicle_info()
                return f"{base_info} | Doors: {self.doors} | Passengers: {self.passenger_capacity}"

            def get_vehicle_type(self):
                return "Car"

        # Motorcycle class - inherits from Vehicle
        class Motorcycle(Vehicle):
            def __init__(self, make, model, year, fuel_type, engine_cc, has_sidecar=False):
                super().__init__(make, model, year, fuel_type)
                self.engine_cc = engine_cc
                self.has_sidecar = has_sidecar
                self._kickstand_down = True

            def raise_kickstand(self):
                if self._kickstand_down:
                    self._kickstand_down = False
                    return "Kickstand raised"
                return "Kickstand is already raised"

            def lower_kickstand(self):
                if not self._kickstand_down:
                    self._kickstand_down = True
                    return "Kickstand lowered"
                return "Kickstand is already lowered"

            # Override with additional safety check
            def start_engine(self):
                if self._kickstand_down:
                    return "Cannot start engine - kickstand is down"
                return super().start_engine()

            def get_vehicle_info(self):
                base_info = super().get_vehicle_info()
                sidecar_info = " with sidecar" if self.has_sidecar else ""
                return f"{base_info} | Engine: {self.engine_cc}cc{sidecar_info}"

            def get_vehicle_type(self):
                return "Motorcycle"

        # Truck class - inherits from Vehicle
        class Truck(Vehicle):
            def __init__(self, make, model, year, fuel_type, cargo_capacity, tow_capacity):
                super().__init__(make, model, year, fuel_type)
                self.cargo_capacity = cargo_capacity  # in tons
                self.tow_capacity = tow_capacity  # in pounds
                self._cargo_loaded = 0

            def load_cargo(self, weight):
                if weight > 0:
                    if self._cargo_loaded + weight <= self.cargo_capacity:
                        self._cargo_loaded += weight
                        return f"Loaded {weight} tons. Total cargo: {self._cargo_loaded} tons"
                    return f"Cannot load {weight} tons - exceeds capacity"
                return "Cargo weight must be positive"

            def unload_cargo(self, weight):
                if weight > 0:
                    if self._cargo_loaded >= weight:
                        self._cargo_loaded -= weight
                        return f"Unloaded {weight} tons. Remaining cargo: {self._cargo_loaded} tons"
                    return f"Cannot unload {weight} tons - only {self._cargo_loaded} tons loaded"
                return "Cargo weight must be positive"

            # Override with truck-specific behavior
            def start_engine(self):
                base_result = super().start_engine()
                if "started" in base_result:
                    cargo_info = f" with {self._cargo_loaded} tons of cargo" if self._cargo_loaded > 0 else ""
                    return f"{base_result} - Truck ready{cargo_info}"
                return base_result

            def get_vehicle_info(self):
                base_info = super().get_vehicle_info()
                return (f"{base_info} | Cargo: {self._cargo_loaded}/{self.cargo_capacity} tons | "
                        f"Tow: {self.tow_capacity} lbs")

            def get_vehicle_type(self):
                return "Truck"

        # SportsCar class - inherits from Car (multi-level inheritance)
        class SportsCar(Car):
            def __init__(self, make, model, year, fuel_type, doors, passenger_capacity, top_speed):
                super().__init__(make, model, year, fuel_type, doors, passenger_capacity)
                self.top_speed = top_speed
                self._sports_mode = False

            def enable_sports_mode(self):
                if not self._sports_mode:
                    self._sports_mode = True
                    return "Sports mode enabled - enhanced performance!"
                return "Sports mode is already enabled"

            def disable_sports_mode(self):
                if self._sports_mode:
                    self._sports_mode = False
                    return "Sports mode disabled"
                return "Sports mode is already disabled"

            # Override with sports car specific behavior
            def start_engine(self):
                base_result = super().start_engine()
                if "started" in base_result and self._sports_mode:
                    return f"{base_result} - Sports mode active! Ready for high performance"
                return base_result

            def get_vehicle_info(self):
                base_info = super().get_vehicle_info()
                sports_status = " (Sports Mode)" if self._sports_mode else ""
                return f"{base_info} | Top Speed: {self.top_speed} mph{sports_status}"

            def get_vehicle_type(self):
                return "Sports Car"

        # Demonstrate the vehicle hierarchy
        print("Creating vehicles from the hierarchy:")

        # Create instances of each vehicle type
        sedan = Car("Toyota", "Camry", 2023, "Gasoline", 4, 5)
        motorcycle = Motorcycle(
            "Harley-Davidson", "Sportster", 2022, "Gasoline", 1200)
        truck = Truck("Ford", "F-150", 2023, "Diesel", 2.5, 11000)
        sports_car = SportsCar("Porsche", "911", 2024,
                               "Premium Gasoline", 2, 2, 182)

        vehicles = [sedan, motorcycle, truck, sports_car]

        print("\nVehicle Information:")
        for vehicle in vehicles:
            print(f"- {vehicle.get_vehicle_info()}")

        # Demonstrate polymorphic behavior
        print("\n" + "-" * 40)
        print("Polymorphic Operations")
        print("-" * 40)

        def operate_vehicle(vehicle):
            """Polymorphic function that works with any Vehicle subclass"""
            print(f"\nOperating {vehicle.get_vehicle_type()}:")

            # These methods work on any Vehicle subclass
            print(f"  {vehicle.start_engine()}")

            # Vehicle-specific methods (polymorphism in action)
            if isinstance(vehicle, Motorcycle):
                print(f"  {vehicle.raise_kickstand()}")
                # Try again after raising kickstand
                print(f"  {vehicle.start_engine()}")
            elif isinstance(vehicle, SportsCar):
                print(f"  {vehicle.enable_sports_mode()}")
                # Try again with sports mode
                print(f"  {vehicle.start_engine()}")

            print(f"  {vehicle.drive(50)}")
            print(f"  {vehicle.stop_engine()}")

            # Vehicle-specific operations
            if isinstance(vehicle, Car):
                print(f"  {vehicle.open_trunk()}")
            elif isinstance(vehicle, Truck):
                print(f"  {vehicle.load_cargo(1.2)}")
            elif isinstance(vehicle, Motorcycle):
                print(f"  {vehicle.lower_kickstand()}")

        # Test each vehicle type
        for vehicle in vehicles:
            operate_vehicle(vehicle)

        # Demonstrate inheritance hierarchy
        print("\n" + "-" * 40)
        print("Inheritance Hierarchy Analysis")
        print("-" * 40)

        print(f"Vehicle classes MRO:")
        print(f"  Car: {Car.__mro__}")
        print(f"  Motorcycle: {Motorcycle.__mro__}")
        print(f"  Truck: {Truck.__mro__}")
        print(f"  SportsCar: {SportsCar.__mro__}")

        print(f"\nInheritance relationships:")
        print(f"  Is SportsCar a Car? {issubclass(SportsCar, Car)}")
        print(f"  Is SportsCar a Vehicle? {issubclass(SportsCar, Vehicle)}")
        print(f"  Is Car a Vehicle? {issubclass(Car, Vehicle)}")
        print(f"  Is Truck a Car? {issubclass(Truck, Car)}")

        # Utility function demonstrating polymorphism
        print("\n" + "-" * 40)
        print("Polymorphic Utility Functions")
        print("-" * 40)

        def get_fleet_statistics(vehicle_list):
            """Calculate statistics for a fleet of vehicles"""
            total_mileage = 0
            vehicle_types = {}

            for vehicle in vehicle_list:
                # Access protected attribute (in real code, use getter method)
                total_mileage += vehicle._mileage
                vehicle_type = vehicle.get_vehicle_type()
                vehicle_types[vehicle_type] = vehicle_types.get(
                    vehicle_type, 0) + 1

            print(f"Fleet Statistics:")
            print(f"  Total vehicles: {len(vehicle_list)}")
            print(f"  Total mileage: {total_mileage} miles")
            print(f"  Vehicle type distribution: {vehicle_types}")

            # Find vehicle with highest theoretical value (simple heuristic)
            if vehicle_list:
                newest_vehicle = max(vehicle_list, key=lambda v: v.year)
                print(f"  Newest vehicle: {newest_vehicle.get_display_name()}")

        get_fleet_statistics(vehicles)


class PracticeExercises:
    """Additional practice exercises for inheritance and polymorphism"""

    def animal_hierarchy_exercise(self):
        """Animal class hierarchy with polymorphism"""
        print("\n" + "=" * 50)
        print("Animal Hierarchy Exercise")
        print("=" * 50)

        class Animal:
            def __init__(self, name, habitat):
                self.name = name
                self.habitat = habitat

            def speak(self):
                return "Some generic animal sound"

            def move(self):
                return f"{self.name} is moving"

            def get_info(self):
                return f"{self.name} lives in {self.habitat}"

        class Mammal(Animal):
            def __init__(self, name, habitat, fur_color):
                super().__init__(name, habitat)
                self.fur_color = fur_color
                self._is_warm_blooded = True

            def give_birth(self):
                return f"{self.name} gives birth to live young"

            def get_info(self):
                return f"{super().get_info()} and has {self.fur_color} fur"

        class Bird(Animal):
            def __init__(self, name, habitat, wingspan):
                super().__init__(name, habitat)
                self.wingspan = wingspan
                self._can_fly = True

            def fly(self):
                if self._can_fly:
                    return f"{self.name} is flying with {self.wingspan}cm wingspan"
                return f"{self.name} cannot fly"

            def get_info(self):
                return f"{super().get_info()} and has {self.wingspan}cm wingspan"

        class Fish(Animal):
            def __init__(self, name, habitat, water_type):
                super().__init__(name, habitat)
                self.water_type = water_type

            def swim(self):
                return f"{self.name} is swimming in {self.water_type} water"

            def get_info(self):
                return f"{super().get_info()} in {self.water_type} water"

        # Specific animal types
        class Dog(Mammal):
            def __init__(self, name, breed):
                super().__init__(name, "land", "varies")
                self.breed = breed

            def speak(self):
                return "Woof!"

            def fetch(self):
                return f"{self.name} is fetching"

        class Eagle(Bird):
            def __init__(self, name):
                super().__init__(name, "mountains", 200)

            def speak(self):
                return "Screech!"

            def hunt(self):
                return f"{self.name} is hunting from the sky"

        class Salmon(Fish):
            def __init__(self, name):
                super().__init__(name, "rivers and oceans", "fresh and salt")

            def speak(self):
                return "Blub blub"

            def migrate(self):
                return f"{self.name} is migrating upstream"

        # Demonstrate the hierarchy
        animals = [
            Dog("Buddy", "Golden Retriever"),
            Eagle("Thunder"),
            Salmon("Swift")
        ]

        print("Animal behaviors (polymorphism):")
        for animal in animals:
            print(f"\n{animal.get_info()}")
            print(f"  Sound: {animal.speak()}")
            print(f"  Movement: {animal.move()}")

            # Type-specific behaviors
            if isinstance(animal, Dog):
                print(f"  Special: {animal.fetch()}")
            elif isinstance(animal, Eagle):
                print(f"  Special: {animal.hunt()}")
                print(f"  Flying: {animal.fly()}")
            elif isinstance(animal, Salmon):
                print(f"  Special: {animal.migrate()}")
                print(f"  Swimming: {animal.swim()}")

        # Polymorphic function
        def make_animals_speak(animal_list):
            return [animal.speak() for animal in animal_list]

        sounds = make_animals_speak(animals)
        print(f"\nAll animal sounds: {sounds}")


def main():
    """Main execution function"""
    print("DAY 15: ADVANCED OOP - INHERITANCE AND POLYMORPHISM")
    print("=" * 70)

    # Initialize classes
    inheritance_demo = InheritanceFundamentals()
    vehicle_project = VehicleHierarchyProject()
    practice_exercises = PracticeExercises()

    # Demonstrate inheritance concepts
    inheritance_demo.demonstrate_single_inheritance()
    inheritance_demo.demonstrate_multiple_inheritance()
    inheritance_demo.demonstrate_polymorphism()

    # Vehicle hierarchy project
    print("\n" + "=" * 70)
    print("PRACTICE PROJECT: VEHICLE HIERARCHY")
    print("=" * 70)

    vehicle_project.create_vehicle_hierarchy()

    # Additional practice exercises
    print("\n" + "=" * 70)
    print("ADDITIONAL PRACTICE EXERCISES")
    print("=" * 70)

    practice_exercises.animal_hierarchy_exercise()

    print("\n" + "=" * 70)
    print("DAY 15 COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("Key concepts mastered:")
    print("- Single and multiple inheritance")
    print("- Method overriding with super()")
    print("- Polymorphism in practice")
    print("- Method Resolution Order (MRO)")
    print("- Building complex class hierarchies")


if __name__ == "__main__":
    main()
