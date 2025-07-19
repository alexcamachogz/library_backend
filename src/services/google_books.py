import sys

import requests
from src.utils.config import GOOGLE_BOOKS_BASE_URL

class GoogleBooksService:
    @staticmethod
    def get_book_by_isbn(isbn):
        """
        Query the Google Books API using ISBN
        Returns the book's data or None if not found
        """
        try:
            # Build URL
            url = f"{GOOGLE_BOOKS_BASE_URL}?q=isbn:{isbn}"

            # Make GET request
            response = requests.get(url, timeout=10)
            response.raise_for_status() # Throw an exception if an HTTP error occur

            data = response.json()

            # Verify if the response has information
            if data.get('totalItems', 0) == 0:
                return None

            # Ger the first book
            book_data = data['items'][0]['volumeInfo']

            # Mapping data
            return GoogleBooksService._map_book_data(book_data, isbn)

        except requests.exceptions.RequestException as e:
            print(f"Error querying Google Books API: {e}")
            return None
        except KeyError as e:
            print(f"Error processing data from Google Books: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error: {e}")
            return None

    @staticmethod
    def _map_book_data(book_data, isbn):
        """
        Map Google Books data to our MongoDB schema
        """
        return {
            'isbn': isbn,
            'title': book_data.get('title', ''),
            'authors': book_data.get('authors', []),
            'description': book_data.get('description', ''),
            'categories': book_data.get('categories', []),
            'page_count': book_data.get('pageCount'),
            'cover_image': GoogleBooksService._get_cover_image(book_data),
            'published_date': book_data.get('publishedDate', ''),
            'publisher': book_data.get('publisher', ''),
            'language': book_data.get('language', '')
        }

    @staticmethod
    def _get_cover_image(book_data):
        """
        Get the best image quality available
        """
        image_links = book_data.get('imageLinks', {})

        # Priority: extraLarge > large > medium > small > thumbnail
        for size in ['extraLarge', 'large', 'medium', 'small', 'thumbnail']:
            if size in image_links:
                return image_links[size]

        return ''
