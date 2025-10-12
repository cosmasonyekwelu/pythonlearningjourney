"""
Book module defining the core book classes with inheritance hierarchy.
Demonstrates OOP principles including inheritance, encapsulation, and polymorphism.
"""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import uuid


class Book(ABC):
    """Abstract base class for all book types in the library."""

    def __init__(self, title: str, author: str, isbn: str, genre: str,
                 publication_year: int, **kwargs):
        """
        Initialize a book with common attributes.

        Args:
            title (str): Book title
            author (str): Book author
            isbn (str): International Standard Book Number
            genre (str): Book genre/category
            publication_year (int): Year of publication
            **kwargs: Additional book attributes
        """
        self._id = str(uuid.uuid4())
        self.title = title
        self.author = author
        self.isbn = isbn
        self.genre = genre
        self.publication_year = publication_year
        self.is_available = True
        self.date_added = datetime.now()
        self.borrowing_history = []

        # Set additional attributes from kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

    @abstractmethod
    def get_details(self) -> Dict[str, Any]:
        """Abstract method to get book details - must be implemented by subclasses."""
        pass

    def borrow(self, borrower: str, days: int = 14) -> bool:
        """
        Borrow the book if available.

        Args:
            borrower (str): Name of the person borrowing the book
            days (int): Number of days to borrow for

        Returns:
            bool: True if book was successfully borrowed, False otherwise
        """
        if not self.is_available:
            return False

        self.is_available = False
        borrow_record = {
            'borrower': borrower,
            'borrow_date': datetime.now().isoformat(),
            'due_date': (datetime.now() + timedelta(days=days)).isoformat(),
            'return_date': None
        }
        self.borrowing_history.append(borrow_record)
        return True

    def return_book(self) -> bool:
        """
        Return a borrowed book.

        Returns:
            bool: True if book was successfully returned, False otherwise
        """
        if self.is_available:
            return False

        self.is_available = True
        if self.borrowing_history:
            self.borrowing_history[-1]['return_date'] = datetime.now().isoformat()
        return True

    def is_overdue(self) -> bool:
        """Check if the book is currently overdue."""
        if self.is_available or not self.borrowing_history:
            return False

        current_borrow = self.borrowing_history[-1]
        if current_borrow['return_date'] is not None:
            return False

        due_date = datetime.fromisoformat(current_borrow['due_date'])
        return datetime.now() > due_date

    def to_dict(self) -> Dict[str, Any]:
        """Convert book to dictionary for serialization."""
        return {
            'id': self._id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'is_available': self.is_available,
            'date_added': self.date_added.isoformat(),
            'borrowing_history': self.borrowing_history,
            'type': self.__class__.__name__
        }

    def __str__(self) -> str:
        """String representation of the book."""
        status = "Available" if self.is_available else "Borrowed"
        return f"'{self.title}' by {self.author} ({self.publication_year}) - {status}"

    def __repr__(self) -> str:
        """Detailed representation of the book."""
        return f"Book(title='{self.title}', author='{self.author}', isbn='{self.isbn}')"


class EBook(Book):
    """EBook subclass representing digital books."""

    def __init__(self, title: str, author: str, isbn: str, genre: str,
                 publication_year: int, file_size: float, file_format: str,
                 download_link: Optional[str] = None, **kwargs):
        """
        Initialize an eBook.

        Args:
            file_size (float): Size of the eBook file in MB
            file_format (str): Format of the eBook (PDF, EPUB, etc.)
            download_link (str, optional): Link to download the eBook
        """
        super().__init__(title, author, isbn, genre, publication_year, **kwargs)
        self.file_size = file_size
        self.file_format = file_format.upper()
        self.download_link = download_link
        self.reading_progress = 0  # Percentage

    def get_details(self) -> Dict[str, Any]:
        """Get comprehensive eBook details."""
        base_details = {
            'id': self._id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'type': 'EBook',
            'is_available': self.is_available,
            'file_size_mb': self.file_size,
            'file_format': self.file_format,
            'download_link': self.download_link,
            'reading_progress': self.reading_progress
        }

        if self.borrowing_history:
            current_borrow = self.borrowing_history[-1]
            base_details['current_borrower'] = current_borrow['borrower']
            base_details['due_date'] = current_borrow['due_date']

        return base_details

    def update_reading_progress(self, progress: int) -> bool:
        """
        Update reading progress percentage.

        Args:
            progress (int): Reading progress percentage (0-100)

        Returns:
            bool: True if progress was updated successfully
        """
        if 0 <= progress <= 100:
            self.reading_progress = progress
            return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert eBook to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'file_size': self.file_size,
            'file_format': self.file_format,
            'download_link': self.download_link,
            'reading_progress': self.reading_progress
        })
        return base_dict

    def __str__(self) -> str:
        """String representation of the eBook."""
        base_str = super().__str__()
        return f"{base_str} [EBook - {self.file_format}]"


class PrintBook(Book):
    """PrintBook subclass representing physical books."""

    def __init__(self, title: str, author: str, isbn: str, genre: str,
                 publication_year: int, page_count: int, condition: str,
                 location: str, **kwargs):
        """
        Initialize a print book.

        Args:
            page_count (int): Number of pages in the book
            condition (str): Physical condition of the book
            location (str): Location in the library
        """
        super().__init__(title, author, isbn, genre, publication_year, **kwargs)
        self.page_count = page_count
        self.condition = condition  # New, Good, Fair, Poor
        self.location = location
        self.times_repaired = 0

    def get_details(self) -> Dict[str, Any]:
        """Get comprehensive print book details."""
        base_details = {
            'id': self._id,
            'title': self.title,
            'author': self.author,
            'isbn': self.isbn,
            'genre': self.genre,
            'publication_year': self.publication_year,
            'type': 'PrintBook',
            'is_available': self.is_available,
            'page_count': self.page_count,
            'condition': self.condition,
            'location': self.location,
            'times_repaired': self.times_repaired
        }

        if self.borrowing_history:
            current_borrow = self.borrowing_history[-1]
            base_details['current_borrower'] = current_borrow['borrower']
            base_details['due_date'] = current_borrow['due_date']

        return base_details

    def update_condition(self, new_condition: str) -> bool:
        """
        Update the physical condition of the book.

        Args:
            new_condition (str): New condition rating

        Returns:
            bool: True if condition was updated successfully
        """
        valid_conditions = ['New', 'Good', 'Fair', 'Poor']
        if new_condition in valid_conditions:
            self.condition = new_condition
            return True
        return False

    def mark_repaired(self) -> None:
        """Increment the repair counter."""
        self.times_repaired += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert print book to dictionary for serialization."""
        base_dict = super().to_dict()
        base_dict.update({
            'page_count': self.page_count,
            'condition': self.condition,
            'location': self.location,
            'times_repaired': self.times_repaired
        })
        return base_dict

    def __str__(self) -> str:
        """String representation of the print book."""
        base_str = super().__str__()
        return f"{base_str} [Print - {self.condition} condition]"


def create_book(book_type: str, **kwargs) -> Book:
    """
    Factory function to create book instances.

    Args:
        book_type (str): Type of book to create ('ebook' or 'print')
        **kwargs: Book attributes

    Returns:
        Book: Book instance of the specified type

    Raises:
        ValueError: If book_type is invalid or required fields are missing
    """
    required_fields = ['title', 'author', 'isbn', 'genre', 'publication_year']

    for field in required_fields:
        if field not in kwargs:
            raise ValueError(f"Missing required field: {field}")

    if book_type.lower() == 'ebook':
        ebook_required = ['file_size', 'file_format']
        for field in ebook_required:
            if field not in kwargs:
                raise ValueError(f"EBook requires field: {field}")
        return EBook(**kwargs)

    elif book_type.lower() == 'print':
        print_required = ['page_count', 'condition', 'location']
        for field in print_required:
            if field not in kwargs:
                raise ValueError(f"PrintBook requires field: {field}")
        return PrintBook(**kwargs)

    else:
        raise ValueError(
            f"Invalid book type: {book_type}. Use 'ebook' or 'print'.")
