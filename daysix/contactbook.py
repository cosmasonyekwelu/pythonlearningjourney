"""
Day 6 Mini-Project: Contact Book System
Python Learning Journey - File Persistence & Search Algorithms
"""

import csv
import os
from typing import List, Dict, Optional


class ContactBook:
    def __init__(self, filename: str = "contacts.csv"):
        self.filename = filename
        self.contacts = []
        self.fieldnames = ['name', 'phone', 'email']
        self.load_contacts()

    def load_contacts(self):
        """Load contacts from CSV file"""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'r', encoding='utf-8') as file:
                    csv_reader = csv.DictReader(file)
                    self.contacts = list(csv_reader)
                print(
                    f"✅ Loaded {len(self.contacts)} contacts from {self.filename}")
            except Exception as e:
                print(f"❌ Error loading contacts: {e}")
                self.contacts = []
        else:
            print("📝 No existing contact file found. Starting fresh.")
            self.contacts = []

    def save_contacts(self):
        """Save contacts to CSV file"""
        try:
            with open(self.filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                writer.writeheader()
                writer.writerows(self.contacts)
            return True
        except Exception as e:
            print(f"❌ Error saving contacts: {e}")
            return False

    def add_contact(self, name: str, phone: str, email: str) -> bool:
        """Add a new contact with validation"""
        # Basic validation
        if not name or not phone:
            print("❌ Name and phone are required!")
            return False

        # Check for duplicates
        if self.linear_search_by_name(name) != -1:
            print(f"❌ Contact '{name}' already exists!")
            return False

        new_contact = {
            'name': name.strip(),
            'phone': phone.strip(),
            'email': email.strip() if email else ''
        }

        self.contacts.append(new_contact)

        # Keep contacts sorted by name for efficient binary search
        self.contacts.sort(key=lambda x: x['name'].lower())

        if self.save_contacts():
            print(f"✅ Contact '{name}' added successfully!")
            return True
        else:
            self.contacts.pop()  # Remove if save failed
            return False

    def linear_search_by_name(self, name: str) -> int:
        """Linear search for contact by name (case-insensitive)"""
        search_name = name.lower().strip()
        for i, contact in enumerate(self.contacts):
            if contact['name'].lower() == search_name:
                return i
        return -1

    def binary_search_by_name(self, name: str) -> int:
        """Binary search for contact by name (requires sorted list)"""
        search_name = name.lower().strip()
        low = 0
        high = len(self.contacts) - 1

        while low <= high:
            mid = (low + high) // 2
            mid_name = self.contacts[mid]['name'].lower()

            if mid_name == search_name:
                return mid
            elif mid_name < search_name:
                low = mid + 1
            else:
                high = mid - 1

        return -1

    def search_contact(self, name: str) -> Optional[Dict[str, str]]:
        """Search for contact using both algorithms and compare"""
        print(f"\n🔍 Searching for '{name}'...")

        # Linear search
        linear_index = self.linear_search_by_name(name)

        # Binary search (contacts are kept sorted)
        binary_index = self.binary_search_by_name(name)

        if linear_index != -1 and binary_index != -1:
            contact = self.contacts[binary_index]
            print(
                f"✅ Found: {contact['name']} | {contact['phone']} | {contact['email']}")

            # Demonstrate algorithm difference
            if linear_index == binary_index:
                print("   Both algorithms found the same contact!")
            return contact
        else:
            print(f"❌ Contact '{name}' not found.")
            return None

    def display_all_contacts(self):
        """Display all contacts in a formatted table"""
        if not self.contacts:
            print("📭 No contacts in the address book.")
            return

        print(f"\n📋 CONTACT BOOK ({len(self.contacts)} contacts)")
        print("=" * 60)
        print(f"{'Name':<20} {'Phone':<15} {'Email':<25}")
        print("-" * 60)

        for contact in self.contacts:
            name = contact['name'][:19]  # Truncate if too long
            phone = contact['phone'][:14]
            email = contact['email'][:24] if contact['email'] else "N/A"
            print(f"{name:<20} {phone:<15} {email:<25}")

    def delete_contact(self, name: str) -> bool:
        """Delete a contact by name"""
        index = self.linear_search_by_name(name)
        if index == -1:
            print(f"❌ Contact '{name}' not found.")
            return False

        deleted_contact = self.contacts.pop(index)
        if self.save_contacts():
            print(
                f"✅ Contact '{deleted_contact['name']}' deleted successfully.")
            return True
        else:
            # Restore if save failed
            self.contacts.insert(index, deleted_contact)
            return False

    def update_contact(self, name: str, new_phone: str = None, new_email: str = None) -> bool:
        """Update contact information"""
        index = self.linear_search_by_name(name)
        if index == -1:
            print(f"❌ Contact '{name}' not found.")
            return False

        if new_phone:
            self.contacts[index]['phone'] = new_phone
        if new_email:
            self.contacts[index]['email'] = new_email

        if self.save_contacts():
            print(f"✅ Contact '{name}' updated successfully.")
            return True
        else:
            print("❌ Failed to update contact.")
            return False


def demo_contact_book():
    """Demonstrate the contact book system"""
    print("🚀 CONTACT BOOK SYSTEM DEMONSTRATION")
    print("=" * 50)

    # Create contact book instance
    contact_book = ContactBook()

    # Add sample contacts
    sample_contacts = [
        ("Alice Johnson", "123-456-7890", "alice@email.com"),
        ("Bob Smith", "234-567-8901", "bob@email.com"),
        ("Charlie Brown", "345-678-9012", "charlie@email.com"),
        ("Diana Prince", "456-789-0123", "diana@email.com")
    ]

    for name, phone, email in sample_contacts:
        contact_book.add_contact(name, phone, email)

    # Display all contacts
    contact_book.display_all_contacts()

    # Demonstrate search
    contact_book.search_contact("Bob Smith")
    contact_book.search_contact("Nonexistent Person")

    return contact_book


def interactive_contact_book():
    """Interactive contact book application"""
    contact_book = ContactBook()

    while True:
        print("\n" + "=" * 40)
        print("📞 CONTACT BOOK SYSTEM")
        print("=" * 40)
        print("1. Add Contact")
        print("2. Search Contact")
        print("3. Display All Contacts")
        print("4. Update Contact")
        print("5. Delete Contact")
        print("6. Exit")

        choice = input("\nEnter your choice (1-6): ").strip()

        if choice == "1":
            print("\n➕ ADD NEW CONTACT")
            name = input("Name: ").strip()
            phone = input("Phone: ").strip()
            email = input("Email (optional): ").strip()
            contact_book.add_contact(name, phone, email)

        elif choice == "2":
            name = input("\n🔍 Enter name to search: ").strip()
            contact_book.search_contact(name)

        elif choice == "3":
            contact_book.display_all_contacts()

        elif choice == "4":
            name = input("\n✏️  Enter name to update: ").strip()
            new_phone = input(
                "New phone (press Enter to keep current): ").strip()
            new_email = input(
                "New email (press Enter to keep current): ").strip()

            if new_phone or new_email:
                contact_book.update_contact(
                    name, new_phone or None, new_email or None)
            else:
                print("❌ No changes provided.")

        elif choice == "5":
            name = input("\n🗑️  Enter name to delete: ").strip()
            if name:
                contact_book.delete_contact(name)

        elif choice == "6":
            print("Thank you for using Contact Book!")
            break

        else:
            print("❌ Invalid choice! Please try again.")


if __name__ == "__main__":
    # Run demonstration
    demo_contact_book()

    # Start interactive version
    print("\n" + "=" * 50)
    print("🎮 STARTING INTERACTIVE CONTACT BOOK")
    print("=" * 50)
    interactive_contact_book()
