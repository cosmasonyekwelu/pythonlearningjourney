"""
Day 17: File I/O and Data Persistence
Python Learning Journey - Reading, Writing, and Storing Structured Data
"""

import json
import csv
import os
from datetime import datetime


class FileOperations:
    """Comprehensive file operations and handling"""

    def demonstrate_basic_file_operations(self):
        """Basic file operations with different modes"""
        print("=" * 60)
        print("Basic File Operations")
        print("=" * 60)

        # File writing modes
        print("File Writing Modes:")
        print("  'w' - Write (overwrites existing file)")
        print("  'a' - Append (adds to existing file)")
        print("  'x' - Exclusive creation (fails if file exists)")

        # Write mode example
        print("\n1. Writing to a file ('w' mode):")
        try:
            with open('sample.txt', 'w', encoding='utf-8') as file:
                file.write("Hello, World!\n")
                file.write("This is a sample text file.\n")
                file.write("Line 3 of our file.\n")
            print("  File 'sample.txt' created successfully")
        except IOError as e:
            print(f"  Error writing file: {e}")

        # Read mode example
        print("\n2. Reading from a file ('r' mode):")
        try:
            with open('sample.txt', 'r', encoding='utf-8') as file:
                content = file.read()
                print("  File content:")
                print("  " + content.replace('\n', '\n  '))
        except FileNotFoundError:
            print("  File not found")
        except IOError as e:
            print(f"  Error reading file: {e}")

        # Append mode example
        print("\n3. Appending to a file ('a' mode):")
        try:
            with open('sample.txt', 'a', encoding='utf-8') as file:
                file.write("This line was appended.\n")
                file.write("Another appended line.\n")
            print("  Content appended successfully")
        except IOError as e:
            print(f"  Error appending to file: {e}")

        # Read lines example
        print("\n4. Reading file line by line:")
        try:
            with open('sample.txt', 'r', encoding='utf-8') as file:
                print("  File lines:")
                for i, line in enumerate(file, 1):
                    print(f"  Line {i}: {line.strip()}")
        except FileNotFoundError:
            print("  File not found")

        # Context manager benefits
        print("\n5. Context Manager Benefits:")
        print("  - Automatic file closing")
        print("  - Exception handling")
        print("  - Cleaner code")
        print("  - Resource management")

    def demonstrate_json_operations(self):
        """JSON serialization and deserialization"""
        print("\n" + "=" * 60)
        print("JSON Operations")
        print("=" * 60)

        # Sample data structure
        sample_data = {
            "users": [
                {
                    "id": 1,
                    "name": "Alice Johnson",
                    "email": "alice@example.com",
                    "age": 28,
                    "is_active": True,
                    "join_date": "2023-01-15"
                },
                {
                    "id": 2,
                    "name": "Bob Smith",
                    "email": "bob@example.com",
                    "age": 32,
                    "is_active": True,
                    "join_date": "2023-02-20"
                },
                {
                    "id": 3,
                    "name": "Charlie Brown",
                    "email": "charlie@example.com",
                    "age": 25,
                    "is_active": False,
                    "join_date": "2023-03-10"
                }
            ],
            "metadata": {
                "total_users": 3,
                "active_users": 2,
                "created": datetime.now().isoformat()
            }
        }

        # Writing JSON to file
        print("1. Writing JSON data to file:")
        try:
            with open('users.json', 'w', encoding='utf-8') as file:
                json.dump(sample_data, file, indent=2, ensure_ascii=False)
            print("  JSON file 'users.json' created successfully")
        except IOError as e:
            print(f"  Error writing JSON: {e}")

        # Reading JSON from file
        print("\n2. Reading JSON data from file:")
        try:
            with open('users.json', 'r', encoding='utf-8') as file:
                loaded_data = json.load(file)

            print("  Loaded data structure:")
            print(f"  Total users: {loaded_data['metadata']['total_users']}")
            print(f"  Active users: {loaded_data['metadata']['active_users']}")
            print("\n  User details:")
            for user in loaded_data['users']:
                status = "Active" if user['is_active'] else "Inactive"
                print(f"    - {user['name']} ({user['email']}) - {status}")

        except FileNotFoundError:
            print("  JSON file not found")
        except json.JSONDecodeError as e:
            print(f"  Error parsing JSON: {e}")
        except IOError as e:
            print(f"  Error reading JSON: {e}")

        # JSON with custom serialization
        print("\n3. Custom JSON serialization:")

        class Person:
            def __init__(self, name, age, email):
                self.name = name
                self.age = age
                self.email = email
                self.created_at = datetime.now()

            def to_dict(self):
                return {
                    'name': self.name,
                    'age': self.age,
                    'email': self.email,
                    'created_at': self.created_at.isoformat()
                }

            @classmethod
            def from_dict(cls, data):
                person = cls(data['name'], data['age'], data['email'])
                person.created_at = datetime.fromisoformat(data['created_at'])
                return person

        # Create and serialize custom objects
        people = [
            Person("John Doe", 30, "john@example.com"),
            Person("Jane Smith", 25, "jane@example.com")
        ]

        # Convert to list of dictionaries
        people_data = [person.to_dict() for person in people]

        try:
            with open('people.json', 'w', encoding='utf-8') as file:
                json.dump(people_data, file, indent=2)
            print("  Custom objects serialized to 'people.json'")
        except IOError as e:
            print(f"  Error writing custom JSON: {e}")

        # Deserialize custom objects
        try:
            with open('people.json', 'r', encoding='utf-8') as file:
                loaded_people_data = json.load(file)

            loaded_people = [Person.from_dict(data)
                             for data in loaded_people_data]
            print("  Custom objects deserialized:")
            for person in loaded_people:
                print(f"    - {person.name}, {person.age} years old")

        except (FileNotFoundError, json.JSONDecodeError, IOError) as e:
            print(f"  Error loading custom objects: {e}")

    def demonstrate_csv_operations(self):
        """CSV file reading and writing"""
        print("\n" + "=" * 60)
        print("CSV Operations")
        print("=" * 60)

        # Sample data for CSV
        employees = [
            ['Name', 'Department', 'Salary', 'Join Date'],
            ['John Doe', 'Engineering', '75000', '2022-01-15'],
            ['Jane Smith', 'Marketing', '65000', '2022-03-20'],
            ['Bob Johnson', 'Sales', '70000', '2021-11-10'],
            ['Alice Brown', 'Engineering', '80000', '2020-05-15'],
            ['Charlie Wilson', 'HR', '60000', '2023-02-28']
        ]

        # Writing CSV with csv.writer
        print("1. Writing CSV with csv.writer:")
        try:
            with open('employees.csv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(employees)
            print("  CSV file 'employees.csv' created successfully")
        except IOError as e:
            print(f"  Error writing CSV: {e}")

        # Reading CSV with csv.reader
        print("\n2. Reading CSV with csv.reader:")
        try:
            with open('employees.csv', 'r', encoding='utf-8') as file:
                reader = csv.reader(file)
                print("  CSV content:")
                for i, row in enumerate(reader):
                    if i == 0:  # Header row
                        print(f"  Header: {', '.join(row)}")
                    else:
                        print(f"  Row {i}: {row}")
        except FileNotFoundError:
            print("  CSV file not found")
        except IOError as e:
            print(f"  Error reading CSV: {e}")

        # Using csv.DictReader and csv.DictWriter
        print("\n3. Using csv.DictReader and csv.DictWriter:")

        # Sample data as dictionaries
        products = [
            {'name': 'Laptop', 'category': 'Electronics',
                'price': '999.99', 'stock': '15'},
            {'name': 'Mouse', 'category': 'Electronics',
                'price': '25.50', 'stock': '45'},
            {'name': 'Notebook', 'category': 'Stationery',
                'price': '5.99', 'stock': '100'},
            {'name': 'Pen', 'category': 'Stationery',
                'price': '1.99', 'stock': '200'}
        ]

        # Write with DictWriter
        try:
            with open('products.csv', 'w', newline='', encoding='utf-8') as file:
                fieldnames = ['name', 'category', 'price', 'stock']
                writer = csv.DictWriter(file, fieldnames=fieldnames)

                writer.writeheader()
                writer.writerows(products)
            print("  Products CSV created with DictWriter")
        except IOError as e:
            print(f"  Error writing products CSV: {e}")

        # Read with DictReader
        try:
            with open('products.csv', 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                print("  Products data:")
                for product in reader:
                    print(
                        f"    - {product['name']}: ${product['price']} ({product['stock']} in stock)")
        except FileNotFoundError:
            print("  Products CSV not found")
        except IOError as e:
            print(f"  Error reading products CSV: {e}")

        # CSV with different delimiters
        print("\n4. CSV with different delimiters:")
        try:
            with open('data.tsv', 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file, delimiter='\t')  # Tab-separated
                writer.writerows(employees)
            print("  Tab-separated file 'data.tsv' created")
        except IOError as e:
            print(f"  Error writing TSV: {e}")

    def demonstrate_configuration_files(self):
        """Configuration file handling"""
        print("\n" + "=" * 60)
        print("Configuration Files")
        print("=" * 60)

        # Sample configuration data
        app_config = {
            "app": {
                "name": "MyPythonApp",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "database": {
                "host": "localhost",
                "port": 5432,
                "name": "mydatabase",
                "username": "admin",
                "timeout": 30
            },
            "features": {
                "enable_export": True,
                "max_file_size": 10485760,
                "allowed_extensions": [".txt", ".csv", ".json"]
            }
        }

        # Write configuration to JSON file
        print("1. Writing configuration to JSON:")
        try:
            with open('config.json', 'w', encoding='utf-8') as file:
                json.dump(app_config, file, indent=2)
            print("  Configuration file 'config.json' created")
        except IOError as e:
            print(f"  Error writing config: {e}")

        # Read and use configuration
        print("\n2. Reading and using configuration:")
        try:
            with open('config.json', 'r', encoding='utf-8') as file:
                config = json.load(file)

            print("  Application Configuration:")
            print(f"    Name: {config['app']['name']}")
            print(f"    Version: {config['app']['version']}")
            print(f"    Debug: {config['app']['debug']}")
            print(f"    Log Level: {config['app']['log_level']}")

            print("\n  Database Configuration:")
            print(f"    Host: {config['database']['host']}")
            print(f"    Port: {config['database']['port']}")
            print(f"    Timeout: {config['database']['timeout']} seconds")

            print("\n  Feature Flags:")
            print(f"    Export Enabled: {config['features']['enable_export']}")
            print(
                f"    Max File Size: {config['features']['max_file_size']} bytes")
            print(
                f"    Allowed Extensions: {', '.join(config['features']['allowed_extensions'])}")

        except FileNotFoundError:
            print("  Configuration file not found")
        except (json.JSONDecodeError, KeyError) as e:
            print(f"  Error reading configuration: {e}")

        # Configuration manager class
        print("\n3. Configuration Manager Class:")

        class ConfigManager:
            def __init__(self, config_file='app_config.json'):
                self.config_file = config_file
                self.config = self._load_config()

            def _load_config(self):
                """Load configuration from file"""
                default_config = {
                    'app': {'name': 'DefaultApp', 'version': '1.0.0'},
                    'settings': {'theme': 'light', 'language': 'en'}
                }

                try:
                    with open(self.config_file, 'r', encoding='utf-8') as file:
                        return json.load(file)
                except FileNotFoundError:
                    print(f"  Config file not found, using defaults")
                    return default_config
                except (json.JSONDecodeError, IOError) as e:
                    print(f"  Error loading config: {e}, using defaults")
                    return default_config

            def save_config(self):
                """Save configuration to file"""
                try:
                    with open(self.config_file, 'w', encoding='utf-8') as file:
                        json.dump(self.config, file, indent=2)
                    print(f"  Configuration saved to {self.config_file}")
                except IOError as e:
                    print(f"  Error saving config: {e}")

            def get(self, section, key, default=None):
                """Get configuration value"""
                try:
                    return self.config[section][key]
                except KeyError:
                    return default

            def set(self, section, key, value):
                """Set configuration value"""
                if section not in self.config:
                    self.config[section] = {}
                self.config[section][key] = value

        # Demonstrate ConfigManager
        config_manager = ConfigManager('app_config.json')

        print("  Current configuration:")
        print(f"    App Name: {config_manager.get('app', 'name')}")
        print(
            f"    Theme: {config_manager.get('settings', 'theme', 'default')}")

        # Update configuration
        config_manager.set('settings', 'theme', 'dark')
        config_manager.set('settings', 'language', 'fr')
        config_manager.save_config()

        print("  Updated configuration saved")


class ContactBookProject:
    """Mini Project: Contact Book with JSON persistence"""

    def create_contact_book(self):
        """Comprehensive contact book with file persistence"""
        print("\n" + "=" * 60)
        print("Contact Book Project")
        print("=" * 60)

        class Contact:
            def __init__(self, name, phone, email, address=""):
                self.name = name
                self.phone = phone
                self.email = email
                self.address = address
                self.created_at = datetime.now()
                self.updated_at = datetime.now()

            def to_dict(self):
                """Convert contact to dictionary for JSON serialization"""
                return {
                    'name': self.name,
                    'phone': self.phone,
                    'email': self.email,
                    'address': self.address,
                    'created_at': self.created_at.isoformat(),
                    'updated_at': self.updated_at.isoformat()
                }

            @classmethod
            def from_dict(cls, data):
                """Create contact from dictionary"""
                contact = cls(data['name'], data['phone'],
                              data['email'], data.get('address', ''))
                contact.created_at = datetime.fromisoformat(data['created_at'])
                contact.updated_at = datetime.fromisoformat(data['updated_at'])
                return contact

            def update(self, **kwargs):
                """Update contact fields"""
                for key, value in kwargs.items():
                    if hasattr(self, key):
                        setattr(self, key, value)
                self.updated_at = datetime.now()

            def __str__(self):
                return f"{self.name} - {self.phone} - {self.email}"

            def __repr__(self):
                return f"Contact('{self.name}', '{self.phone}', '{self.email}')"

        class ContactBook:
            def __init__(self, data_file='contacts.json'):
                self.data_file = data_file
                self.contacts = []
                self._load_contacts()

            def _load_contacts(self):
                """Load contacts from JSON file"""
                try:
                    if os.path.exists(self.data_file):
                        with open(self.data_file, 'r', encoding='utf-8') as file:
                            contacts_data = json.load(file)
                            self.contacts = [Contact.from_dict(
                                data) for data in contacts_data]
                        print(
                            f"  Loaded {len(self.contacts)} contacts from {self.data_file}")
                    else:
                        print(f"  No existing contact file found. Starting fresh.")
                        self.contacts = []
                except (json.JSONDecodeError, IOError, KeyError) as e:
                    print(f"  Error loading contacts: {e}")
                    self.contacts = []

            def _save_contacts(self):
                """Save contacts to JSON file"""
                try:
                    contacts_data = [contact.to_dict()
                                     for contact in self.contacts]
                    with open(self.data_file, 'w', encoding='utf-8') as file:
                        json.dump(contacts_data, file,
                                  indent=2, ensure_ascii=False)
                    return True
                except IOError as e:
                    print(f"  Error saving contacts: {e}")
                    return False

            def add_contact(self, name, phone, email, address=""):
                """Add a new contact"""
                # Basic validation
                if not name or not phone:
                    print("  Error: Name and phone are required")
                    return False

                # Check for duplicate phone number
                for contact in self.contacts:
                    if contact.phone == phone:
                        print(
                            f"  Error: Contact with phone {phone} already exists")
                        return False

                new_contact = Contact(name, phone, email, address)
                self.contacts.append(new_contact)

                if self._save_contacts():
                    print(f"  Contact '{name}' added successfully")
                    return True
                else:
                    self.contacts.pop()  # Remove if save failed
                    return False

            def find_contact(self, search_term):
                """Find contacts by name, phone, or email"""
                results = []
                search_term = search_term.lower()

                for contact in self.contacts:
                    if (search_term in contact.name.lower() or
                        search_term in contact.phone or
                            search_term in contact.email.lower()):
                        results.append(contact)

                return results

            def update_contact(self, phone, **kwargs):
                """Update existing contact"""
                for contact in self.contacts:
                    if contact.phone == phone:
                        contact.update(**kwargs)
                        if self._save_contacts():
                            print(
                                f"  Contact '{contact.name}' updated successfully")
                            return True
                        return False

                print(f"  Error: Contact with phone {phone} not found")
                return False

            def delete_contact(self, phone):
                """Delete contact by phone number"""
                for i, contact in enumerate(self.contacts):
                    if contact.phone == phone:
                        deleted_name = contact.name
                        self.contacts.pop(i)
                        if self._save_contacts():
                            print(
                                f"  Contact '{deleted_name}' deleted successfully")
                            return True
                        return False

                print(f"  Error: Contact with phone {phone} not found")
                return False

            def list_contacts(self):
                """List all contacts"""
                if not self.contacts:
                    print("  No contacts in the address book")
                    return

                print(f"\n  Contacts ({len(self.contacts)} total):")
                for i, contact in enumerate(self.contacts, 1):
                    print(f"    {i}. {contact.name}")
                    print(f"       Phone: {contact.phone}")
                    print(f"       Email: {contact.email}")
                    if contact.address:
                        print(f"       Address: {contact.address}")
                    print(
                        f"       Added: {contact.created_at.strftime('%Y-%m-%d %H:%M')}")
                    print()

            def export_to_csv(self, csv_file='contacts_export.csv'):
                """Export contacts to CSV file"""
                try:
                    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                        writer = csv.writer(file)
                        writer.writerow(
                            ['Name', 'Phone', 'Email', 'Address', 'Created At'])

                        for contact in self.contacts:
                            writer.writerow([
                                contact.name,
                                contact.phone,
                                contact.email,
                                contact.address,
                                contact.created_at.strftime('%Y-%m-%d %H:%M')
                            ])

                    print(f"  Contacts exported to {csv_file}")
                    return True
                except IOError as e:
                    print(f"  Error exporting to CSV: {e}")
                    return False

            def get_statistics(self):
                """Get contact book statistics"""
                stats = {
                    'total_contacts': len(self.contacts),
                    'with_email': len([c for c in self.contacts if c.email]),
                    'with_address': len([c for c in self.contacts if c.address]),
                    'oldest_contact': min(self.contacts, key=lambda c: c.created_at).name if self.contacts else None,
                    'newest_contact': max(self.contacts, key=lambda c: c.created_at).name if self.contacts else None
                }
                return stats

        # Demonstrate the Contact Book
        print("Initializing Contact Book...")
        contact_book = ContactBook()

        # Add sample contacts
        print("\nAdding sample contacts:")
        contact_book.add_contact(
            "Alice Johnson", "555-0101", "alice@example.com", "123 Main St")
        contact_book.add_contact(
            "Bob Smith", "555-0102", "bob@example.com", "456 Oak Ave")
        contact_book.add_contact(
            "Charlie Brown", "555-0103", "charlie@example.com")
        contact_book.add_contact(
            "Diana Prince", "555-0104", "diana@example.com", "789 Pine Rd")

        # List all contacts
        print("\nListing all contacts:")
        contact_book.list_contacts()

        # Search functionality
        print("\nSearching for 'Alice':")
        results = contact_book.find_contact("alice")
        for contact in results:
            print(f"  Found: {contact}")

        # Update contact
        print("\nUpdating contact:")
        contact_book.update_contact(
            "555-0102", email="bob.smith@example.com", address="456 Oak Avenue, Suite 101")

        # Export to CSV
        print("\nExporting contacts to CSV:")
        contact_book.export_to_csv()

        # Statistics
        print("\nContact Book Statistics:")
        stats = contact_book.get_statistics()
        for key, value in stats.items():
            print(f"  {key.replace('_', ' ').title()}: {value}")

        # Demonstrate persistence by creating a new instance
        print("\nDemonstrating persistence:")
        new_contact_book = ContactBook()
        new_contact_book.list_contacts()

        # Clean up demonstration files
        self._cleanup_demo_files()

    def _cleanup_demo_files(self):
        """Clean up demonstration files"""
        demo_files = [
            'sample.txt', 'users.json', 'people.json', 'employees.csv',
            'products.csv', 'data.tsv', 'config.json', 'app_config.json',
            'contacts.json', 'contacts_export.csv'
        ]

        print("\nCleaning up demonstration files...")
        for file in demo_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"  Removed: {file}")
                except OSError as e:
                    print(f"  Error removing {file}: {e}")


def main():
    """Main execution function"""
    print("DAY 17: FILE I/O AND DATA PERSISTENCE")
    print("=" * 70)

    # Initialize classes
    file_ops = FileOperations()
    contact_project = ContactBookProject()

    # Demonstrate file operations
    file_ops.demonstrate_basic_file_operations()
    file_ops.demonstrate_json_operations()
    file_ops.demonstrate_csv_operations()
    file_ops.demonstrate_configuration_files()

    # Contact Book project
    print("\n" + "=" * 70)
    print("MINI PROJECT: CONTACT BOOK WITH JSON PERSISTENCE")
    print("=" * 70)

    contact_project.create_contact_book()

    print("\n" + "=" * 70)
    print("DAY 17 COMPLETED SUCCESSFULLY!")
    print("=" * 70)
    print("Key concepts mastered:")
    print("- File operations with open() and context managers")
    print("- JSON serialization with json.load() and json.dump()")
    print("- CSV reading/writing with csv module")
    print("- Configuration file handling")
    print("- Data persistence in real-world applications")
    print("- Error handling for robust file operations")


if __name__ == "__main__":
    main()
