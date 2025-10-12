"""
Google Books API integration for book information retrieval and enrichment.
"""

import requests
from typing import Dict, Any, Optional, List
from book import create_book


class GoogleBooksAPI:
    """Client for Google Books API integration."""

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Google Books API client.

        Args:
            api_key (str, optional): Google Books API key for higher rate limits
        """
        self.api_key = api_key

    def search_books(self, query: str, max_results: int = 5) -> List[Dict[str, Any]]:
        """
        Search for books using Google Books API.

        Args:
            query (str): Search query (title, author, ISBN, etc.)
            max_results (int): Maximum number of results to return

        Returns:
            List[Dict[str, Any]]: List of book information dictionaries
        """
        params = {
            'q': query,
            'maxResults': max_results
        }

        if self.api_key:
            params['key'] = self.api_key

        try:
            response = requests.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            books = []

            for item in data.get('items', []):
                book_info = self._parse_book_data(item)
                if book_info:
                    books.append(book_info)

            return books

        except requests.exceptions.RequestException as e:
            print(f"API request failed: {e}")
            return []
        except Exception as e:
            print(f"Error processing API response: {e}")
            return []

    def get_book_by_isbn(self, isbn: str) -> Optional[Dict[str, Any]]:
        """
        Get book information by ISBN.

        Args:
            isbn (str): ISBN to search for

        Returns:
            Optional[Dict[str, Any]]: Book information if found
        """
        return self.search_books(f"isbn:{isbn}", max_results=1)[0] if self.search_books(f"isbn:{isbn}", max_results=1) else None

    def _parse_book_data(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse book data from Google Books API response.

        Args:
            item (Dict[str, Any]): Raw book data from API

        Returns:
            Optional[Dict[str, Any]]: Parsed book information
        """
        try:
            volume_info = item.get('volumeInfo', {})
            industry_identifiers = volume_info.get('industryIdentifiers', [])

            # Extract ISBN
            isbn = None
            for identifier in industry_identifiers:
                if identifier.get('type') in ['ISBN_13', 'ISBN_10']:
                    isbn = identifier.get('identifier')
                    break

            # Extract publication year
            published_date = volume_info.get('publishedDate', '')
            publication_year = int(
                published_date[:4]) if published_date and published_date[:4].isdigit() else None

            book_info = {
                'title': volume_info.get('title', 'Unknown Title'),
                'author': ', '.join(volume_info.get('authors', ['Unknown Author'])),
                'isbn': isbn,
                'genre': ', '.join(volume_info.get('categories', ['Unknown'])),
                'publication_year': publication_year,
                'page_count': volume_info.get('pageCount'),
                'description': volume_info.get('description', ''),
                'publisher': volume_info.get('publisher', ''),
                'cover_image': volume_info.get('imageLinks', {}).get('thumbnail'),
                'api_data': volume_info  # Keep raw data for reference
            }

            return book_info

        except Exception as e:
            print(f"Error parsing book data: {e}")
            return None

    def create_book_from_api(self, book_data: Dict[str, Any], book_type: str = 'print') -> Optional[Any]:
        """
        Create a book instance from API data.

        Args:
            book_data (Dict[str, Any]): Book information from API
            book_type (str): Type of book to create ('ebook' or 'print')

        Returns:
            Optional[Book]: Book instance if created successfully
        """
        try:
            # Common required fields
            common_fields = {
                'title': book_data['title'],
                'author': book_data['author'],
                'isbn': book_data['isbn'] or f"API_{book_data['title'][:10]}",
                'genre': book_data['genre'],
                'publication_year': book_data['publication_year'] or 2023
            }

            if book_type.lower() == 'ebook':
                ebook_fields = {
                    'file_size': 2.5,  # Default value
                    'file_format': 'EPUB',
                    'download_link': None
                }
                return create_book('ebook', **{**common_fields, **ebook_fields})

            elif book_type.lower() == 'print':
                print_fields = {
                    'page_count': book_data.get('page_count', 300),
                    'condition': 'New',
                    'location': 'Shelf A1'
                }
                return create_book('print', **{**common_fields, **print_fields})

            return None

        except Exception as e:
            print(f"Error creating book from API data: {e}")
            return None


def validate_isbn(isbn: str) -> bool:
    """
    Validate ISBN format (basic validation).

    Args:
        isbn (str): ISBN to validate

    Returns:
        bool: True if ISBN format is valid
    """
    # Remove hyphens and spaces
    clean_isbn = isbn.replace('-', '').replace(' ', '')

    # Check length (ISBN-10 or ISBN-13)
    if len(clean_isbn) not in [10, 13]:
        return False

    # Check if all characters are digits (except possibly last character for ISBN-10)
    if len(clean_isbn) == 10:
        if not clean_isbn[:-1].isdigit():
            return False
        if not (clean_isbn[-1].isdigit() or clean_isbn[-1].upper() == 'X'):
            return False
    else:  # ISBN-13
        if not clean_isbn.isdigit():
            return False

    return True
