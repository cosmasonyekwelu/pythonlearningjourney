"""
Python Learning Journey - Day Twenty One
Week Three:  Weekly Review and Project Polish
Date: October 12, 2025
Author: Cosmas Onyekwelu
"""

import os
import sys
from typing import List, Dict, Any
from book import Book, EBook, PrintBook, create_book
from library_manager import LibraryManager
from api_utils import GoogleBooksAPI, validate_isbn


class PersonalLibraryApp:
    """Main application class for Personal Library Manager."""

    def __init__(self):
        """Initialize the application."""
        self.library = LibraryManager()
        self.api_client = GoogleBooksAPI()
        self.running = True

    def display_menu(self) -> None:
        """Display the main menu."""
        print("\n" + "="*50)
        print("PERSONAL LIBRARY MANAGER")
        print("="*50)
        print("1. Add New Book")
        print("2. Remove Book")
        print("3. Search Books")
        print("4. Filter Books")
        print("5. List All Books")
        print("6. Borrow Book")
        print("7. Return Book")
        print("8. View Statistics")
        print("9. Generate Reports")
        print("10. Import from Google Books API")
        print("11. Exit")
        print("="*50)

    def add_book_manual(self) -> None:
        """Add a book manually with user input."""
        print("\n--- Add New Book ---")

        book_type = input("Book type (ebook/print): ").strip().lower()
        if book_type not in ['ebook', 'print']:
            print("Invalid book type. Use 'ebook' or 'print'.")
            return

        title = input("Title: ").strip()
        author = input("Author: ").strip()
        isbn = input("ISBN: ").strip()
        genre = input("Genre: ").strip()

        try:
            publication_year = int(input("Publication Year: ").strip())
        except ValueError:
            print("Invalid year. Using current year.")
            from datetime import datetime
            publication_year = datetime.now().year

        if book_type == 'ebook':
            try:
                file_size = float(input("File Size (MB): ").strip())
            except ValueError:
                print("Invalid file size. Using 2.5 MB.")
                file_size = 2.5

            file_format = input(
                "File Format (PDF/EPUB/MOBI): ").strip().upper()
            download_link = input("Download Link (optional): ").strip() or None

            book_data = {
                'title': title,
                'author': author,
                'isbn': isbn,
                'genre': genre,
                'publication_year': publication_year,
                'file_size': file_size,
                'file_format': file_format,
                'download_link': download_link
            }

        else:  # print book
            try:
                page_count = int(input("Page Count: ").strip())
            except ValueError:
                print("Invalid page count. Using 300.")
                page_count = 300

            condition = input(
                "Condition (New/Good/Fair/Poor): ").strip().capitalize()
            location = input("Location: ").strip()

            book_data = {
                'title': title,
                'author': author,
                'isbn': isbn,
                'genre': genre,
                'publication_year': publication_year,
                'page_count': page_count,
                'condition': condition,
                'location': location
            }

        try:
            book = create_book(book_type, **book_data)
            if self.library.add_book(book):
                print(f"Book '{title}' added successfully!")
            else:
                print("Failed to add book. ISBN might already exist.")
        except ValueError as e:
            print(f"Error creating book: {e}")

    def remove_book(self) -> None:
        """Remove a book from the library."""
        print("\n--- Remove Book ---")
        book_id = input("Enter book ID to remove: ").strip()

        if self.library.remove_book(book_id):
            print("Book removed successfully!")
        else:
            print("Book not found.")

    def search_books(self) -> None:
        """Search for books in the library."""
        print("\n--- Search Books ---")
        query = input("Search query: ").strip()
        field = input(
            "Search field (title/author/genre/isbn) [title]: ").strip() or 'title'

        results = self.library.search_books(query, field)

        if results:
            print(f"\nFound {len(results)} books:")
            for i, book in enumerate(results, 1):
                details = book.get_details()
                print(
                    f"{i}. {details['title']} by {details['author']} ({details['type']}) - ID: {details['id']}")
        else:
            print("No books found.")

    def filter_books(self) -> None:
        """Filter books by various criteria."""
        print("\n--- Filter Books ---")
        print("Leave field blank to skip filter.")

        genre = input("Genre: ").strip() or None
        author = input("Author: ").strip() or None
        book_type = input("Type (ebook/print): ").strip().lower() or None
        available_input = input("Available (yes/no): ").strip().lower()
        available = None
        if available_input == 'yes':
            available = True
        elif available_input == 'no':
            available = False

        filters = {}
        if genre:
            filters['genre'] = genre
        if author:
            filters['author'] = author
        if book_type:
            filters['type'] = book_type
        if available is not None:
            filters['available'] = available

        results = self.library.filter_books(**filters)

        if results:
            print(f"\nFound {len(results)} books:")
            for i, book in enumerate(results, 1):
                details = book.get_details()
                status = "Available" if details['is_available'] else "Borrowed"
                print(
                    f"{i}. {details['title']} by {details['author']} - {status}")
        else:
            print("No books match the filters.")

    def list_all_books(self) -> None:
        """List all books in the library."""
        print("\n--- All Books ---")
        books = self.library.list_all_books()

        if not books:
            print("No books in library.")
            return

        for i, book in enumerate(books, 1):
            status = "Available" if book['is_available'] else "Borrowed"
            print(
                f"{i}. {book['title']} by {book['author']} ({book['type']}) - {status}")

    def borrow_book(self) -> None:
        """Borrow a book from the library."""
        print("\n--- Borrow Book ---")
        book_id = input("Enter book ID: ").strip()
        borrower = input("Borrower name: ").strip()

        try:
            days = int(
                input("Borrow for how many days? [14]: ").strip() or "14")
        except ValueError:
            days = 14

        if self.library.borrow_book(book_id, borrower, days):
            print("Book borrowed successfully!")
        else:
            print("Failed to borrow book. Book might not be available or not found.")

    def return_book(self) -> None:
        """Return a borrowed book."""
        print("\n--- Return Book ---")
        book_id = input("Enter book ID: ").strip()

        if self.library.return_book(book_id):
            print("Book returned successfully!")
        else:
            print("Failed to return book. Book might not be borrowed or not found.")

    def view_statistics(self) -> None:
        """Display library statistics."""
        print("\n--- Library Statistics ---")
        stats = self.library.get_statistics()

        print(f"Total Books: {stats['total_books']}")
        print(f"Available Books: {stats['available_books']}")
        print(f"Borrowed Books: {stats['borrowed_books']}")
        print(f"Overdue Books: {stats['overdue_books']}")
        print(f"E-Books: {stats['ebooks_count']}")
        print(f"Print Books: {stats['print_books_count']}")
        print(f"Utilization Rate: {stats['utilization_rate']}%")

        print("\nGenre Distribution:")
        for genre, count in stats['genre_distribution'].items():
            print(f"  {genre}: {count}")

    def generate_reports(self) -> None:
        """Generate library reports."""
        print("\n--- Generate Reports ---")
        self.library.generate_reports()
        print("Reports generated in 'reports/' directory")
        print(" - summary.txt: Text summary of library statistics")
        print(" - stats.json: JSON data with detailed analytics")

    def import_from_api(self) -> None:
        """Import books using Google Books API."""
        print("\n--- Import from Google Books API ---")
        query = input("Search query (title, author, or ISBN): ").strip()

        if not query:
            print("Please enter a search query.")
            return

        print("Searching...")
        results = self.api_client.search_books(query)

        if not results:
            print("No books found.")
            return

        print(f"\nFound {len(results)} books:")
        for i, book in enumerate(results, 1):
            print(
                f"{i}. {book['title']} by {book['author']} ({book.get('publication_year', 'N/A')})")

        try:
            choice = int(input("\nSelect book to import (number): ").strip())
            if 1 <= choice <= len(results):
                selected_book = results[choice - 1]
                book_type = input(
                    "Book type (ebook/print) [print]: ").strip().lower() or 'print'

                book_instance = self.api_client.create_book_from_api(
                    selected_book, book_type)
                if book_instance and self.library.add_book(book_instance):
                    print(
                        f"Book '{selected_book['title']}' imported successfully!")
                else:
                    print("Failed to import book.")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Invalid input.")

    def run(self) -> None:
        """Run the main application loop."""
        print("Welcome to Personal Library Manager!")

        while self.running:
            self.display_menu()

            try:
                choice = input("\nEnter your choice (1-11): ").strip()

                if choice == '1':
                    self.add_book_manual()
                elif choice == '2':
                    self.remove_book()
                elif choice == '3':
                    self.search_books()
                elif choice == '4':
                    self.filter_books()
                elif choice == '5':
                    self.list_all_books()
                elif choice == '6':
                    self.borrow_book()
                elif choice == '7':
                    self.return_book()
                elif choice == '8':
                    self.view_statistics()
                elif choice == '9':
                    self.generate_reports()
                elif choice == '10':
                    self.import_from_api()
                elif choice == '11':
                    self.running = False
                    print("Thank you for using Personal Library Manager!")
                else:
                    print("Invalid choice. Please enter a number between 1-11.")

            except KeyboardInterrupt:
                print("\n\nOperation cancelled.")
                break
            except Exception as e:
                print(f"An error occurred: {e}")


def main():
    """Main entry point for the application."""
    app = PersonalLibraryApp()
    app.run()


if __name__ == "__main__":
    main()
