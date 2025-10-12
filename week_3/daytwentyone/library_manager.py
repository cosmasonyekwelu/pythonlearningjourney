"""
Library management system implementing search, filtering, and reporting features.
Demonstrates polymorphism and comprehensive data management.
"""

import json
import os
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from book import Book, EBook, PrintBook, create_book


class LibraryManager:
    """Main library management system with data persistence."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the library management system.

        Args:
            data_dir (str): Directory for data storage
        """
        self.data_dir = data_dir
        self.library_file = os.path.join(data_dir, "library.json")
        self.history_file = os.path.join(data_dir, "history.json")
        self.books: List[Book] = []

        # Ensure data directory exists
        os.makedirs(data_dir, exist_ok=True)

        # Load existing data
        self.load_library()

    def add_book(self, book: Book) -> bool:
        """
        Add a book to the library.

        Args:
            book (Book): Book instance to add

        Returns:
            bool: True if book was added successfully
        """
        # Check for duplicate ISBN
        if any(b.isbn == book.isbn for b in self.books):
            return False

        self.books.append(book)
        self.save_library()
        return True

    def remove_book(self, book_id: str) -> bool:
        """
        Remove a book from the library by ID.

        Args:
            book_id (str): Unique ID of the book to remove

        Returns:
            bool: True if book was removed successfully
        """
        for i, book in enumerate(self.books):
            if book._id == book_id:
                removed_book = self.books.pop(i)
                self.save_library()
                return True
        return False

    def find_book_by_id(self, book_id: str) -> Optional[Book]:
        """
        Find a book by its unique ID.

        Args:
            book_id (str): Unique book ID

        Returns:
            Optional[Book]: Book instance if found, None otherwise
        """
        for book in self.books:
            if book._id == book_id:
                return book
        return None

    def search_books(self, query: str, search_field: str = 'title') -> List[Book]:
        """
        Search books by various fields using polymorphism.

        Args:
            query (str): Search query
            search_field (str): Field to search in ('title', 'author', 'genre', 'isbn')

        Returns:
            List[Book]: List of matching books
        """
        query = query.lower()
        results = []

        for book in self.books:
            details = book.get_details()
            field_value = details.get(search_field, '')

            if query in str(field_value).lower():
                results.append(book)

        return results

    def filter_books(self, **filters) -> List[Book]:
        """
        Filter books by multiple criteria using polymorphic methods.

        Args:
            **filters: Filter criteria (genre, author, type, available, etc.)

        Returns:
            List[Book]: List of filtered books
        """
        results = self.books.copy()

        for filter_key, filter_value in filters.items():
            if filter_value is None:
                continue

            filtered_results = []
            for book in results:
                details = book.get_details()

                if filter_key == 'type':
                    if details.get('type', '').lower() == filter_value.lower():
                        filtered_results.append(book)
                elif filter_key == 'available':
                    if details.get('is_available') == filter_value:
                        filtered_results.append(book)
                elif filter_key == 'genre':
                    if filter_value.lower() in details.get('genre', '').lower():
                        filtered_results.append(book)
                elif filter_key in details:
                    if str(details[filter_key]).lower() == str(filter_value).lower():
                        filtered_results.append(book)

            results = filtered_results

        return results

    def borrow_book(self, book_id: str, borrower: str, days: int = 14) -> bool:
        """
        Borrow a book from the library.

        Args:
            book_id (str): ID of the book to borrow
            borrower (str): Name of the borrower
            days (int): Number of days to borrow for

        Returns:
            bool: True if book was successfully borrowed
        """
        book = self.find_book_by_id(book_id)
        if book and book.borrow(borrower, days):
            self.save_library()
            return True
        return False

    def return_book(self, book_id: str) -> bool:
        """
        Return a borrowed book.

        Args:
            book_id (str): ID of the book to return

        Returns:
            bool: True if book was successfully returned
        """
        book = self.find_book_by_id(book_id)
        if book and book.return_book():
            self.save_library()
            return True
        return False

    def get_statistics(self) -> Dict[str, Any]:
        """
        Generate comprehensive library statistics.

        Returns:
            Dict[str, Any]: Library statistics
        """
        total_books = len(self.books)
        available_books = sum(1 for book in self.books if book.is_available)
        borrowed_books = total_books - available_books
        overdue_books = sum(1 for book in self.books if book.is_overdue())

        # Count by type
        ebooks = sum(1 for book in self.books if isinstance(book, EBook))
        print_books = sum(
            1 for book in self.books if isinstance(book, PrintBook))

        # Genre distribution
        genre_count = {}
        for book in self.books:
            genre = book.genre
            genre_count[genre] = genre_count.get(genre, 0) + 1

        # Author statistics
        author_count = {}
        for book in self.books:
            author = book.author
            author_count[author] = author_count.get(author, 0) + 1

        return {
            'total_books': total_books,
            'available_books': available_books,
            'borrowed_books': borrowed_books,
            'overdue_books': overdue_books,
            'ebooks_count': ebooks,
            'print_books_count': print_books,
            'genre_distribution': genre_count,
            'author_distribution': author_count,
            'utilization_rate': round((borrowed_books / total_books * 100) if total_books > 0 else 0, 2)
        }

    def generate_reports(self, reports_dir: str = "reports") -> None:
        """
        Generate text and JSON reports about the library.

        Args:
            reports_dir (str): Directory to save reports
        """
        os.makedirs(reports_dir, exist_ok=True)

        stats = self.get_statistics()

        # Generate text report
        with open(os.path.join(reports_dir, "summary.txt"), "w") as f:
            f.write("LIBRARY SUMMARY REPORT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Total Books: {stats['total_books']}\n")
            f.write(f"Available Books: {stats['available_books']}\n")
            f.write(f"Borrowed Books: {stats['borrowed_books']}\n")
            f.write(f"Overdue Books: {stats['overdue_books']}\n")
            f.write(f"E-Books: {stats['ebooks_count']}\n")
            f.write(f"Print Books: {stats['print_books_count']}\n")
            f.write(f"Utilization Rate: {stats['utilization_rate']}%\n\n")

            f.write("GENRE DISTRIBUTION:\n")
            for genre, count in stats['genre_distribution'].items():
                f.write(f"  {genre}: {count}\n")

            f.write("\nTOP AUTHORS:\n")
            sorted_authors = sorted(stats['author_distribution'].items(),
                                    key=lambda x: x[1], reverse=True)[:5]
            for author, count in sorted_authors:
                f.write(f"  {author}: {count} books\n")

        # Generate JSON report
        with open(os.path.join(reports_dir, "stats.json"), "w") as f:
            json.dump(stats, f, indent=2)

    def save_library(self) -> bool:
        """
        Save library data to JSON file.

        Returns:
            bool: True if save was successful
        """
        try:
            library_data = {
                'books': [book.to_dict() for book in self.books]
            }

            with open(self.library_file, 'w') as f:
                json.dump(library_data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving library: {e}")
            return False

    def load_library(self) -> bool:
        """
        Load library data from JSON file.

        Returns:
            bool: True if load was successful
        """
        try:
            if not os.path.exists(self.library_file):
                return True  # No existing data is not an error

            with open(self.library_file, 'r') as f:
                library_data = json.load(f)

            self.books = []
            for book_data in library_data.get('books', []):
                book_type = book_data.pop('type')
                if book_type == 'EBook':
                    book = EBook(**book_data)
                elif book_type == 'PrintBook':
                    book = PrintBook(**book_data)
                else:
                    continue

                # Restore datetime objects
                book.date_added = datetime.fromisoformat(
                    book_data['date_added'])
                self.books.append(book)

            return True
        except Exception as e:
            print(f"Error loading library: {e}")
            return False

    def list_all_books(self) -> List[Dict[str, Any]]:
        """
        Get detailed information for all books.

        Returns:
            List[Dict[str, Any]]: List of book details
        """
        return [book.get_details() for book in self.books]
