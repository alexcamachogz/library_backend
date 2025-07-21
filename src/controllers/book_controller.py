from flask import request
from flask_restx import Namespace, Resource, fields
from src.services.google_books import GoogleBooksService
from src.services.database import DatabaseService
from src.utils.validators import validate_isbn
from src.models.book import get_book_models

# Create namespace for book operations
api = Namespace('books', description='Book management operations')

# Initialize database service
db_service = DatabaseService()

# Get Swagger models
models = get_book_models(api)

@api.route('/')
class BookList(Resource):
    @api.doc('get_all_books')
    @api.param('limit', 'Maximum number of books to return (1-100)', type=int, default=50)
    @api.param('skip', 'Number of books to skip for pagination', type=int, default=0)
    @api.marshal_with(models['books_list_response'])
    @api.response(200, 'Success')
    @api.response(500, 'Internal server error')
    def get(self):
        """Get all books from library with pagination"""
        try:
            # Get pagination parameters
            limit = request.args.get('limit', 50, type=int)
            skip = request.args.get('skip', 0, type=int)

            # Validate pagination parameters
            if limit <= 0 or limit > 100:
                limit = 50
            if skip < 0:
                skip = 0

            books = db_service.get_all_books(limit=limit, skip=skip)

            return {
                "message": f"Retrieved {len(books)} books",
                "books": books,
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(books)
                }
            }, 200
        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")

    @api.doc('add_book')
    @api.expect(models['book_input'])
    @api.marshal_with(models['success_response'])
    @api.response(201, 'Book added successfully')
    @api.response(400, 'Invalid input')
    @api.response(404, 'Book not found in Google Books')
    @api.response(409, 'Book already exists')
    @api.response(500, 'Internal server error')
    def post(self):
        """Add a book to library by ISBN"""
        try:
            data = request.get_json()

            if not data or 'isbn' not in data:
                api.abort(400, "ISBN is required")

            isbn = data['isbn'].strip()

            # Validate ISBN format
            if not validate_isbn(isbn):
                api.abort(400, "Please provide a valid ISBN-10 or ISBN-13")

            # Check if book already exists
            if db_service.book_exists(isbn):
                api.abort(409, f"A book with ISBN {isbn} is already in your library")

            # Query Google Books API
            book_data = GoogleBooksService.get_book_by_isbn(isbn)

            if not book_data:
                api.abort(404, f"No book found with ISBN {isbn} in Google Books")

            # Save to database
            success = db_service.add_book(book_data)

            if success:
                return {
                    "message": "Book added successfully",
                    "book": book_data
                }, 201
            else:
                api.abort(500, "There was an error saving the book to the database")

        except Exception as e:
            if not str(e).startswith('404') and not str(e).startswith('400') and not str(e).startswith('409'):
                api.abort(500, "An unexpected error occurred")
            raise


@api.route('/<string:isbn>')
@api.param('isbn', 'Book ISBN identifier')
class Book(Resource):
    @api.doc('get_book')
    @api.marshal_with(models['book_output'])
    @api.response(200, 'Success')
    @api.response(400, 'Invalid ISBN format')
    @api.response(404, 'Book not found')
    @api.response(500, 'Internal server error')
    def get(self, isbn):
        """Get a book from library by ISBN"""
        try:
            if not validate_isbn(isbn):
                api.abort(400, "Please provide a valid ISBN-10 or ISBN-13")

            book = db_service.get_book_by_isbn(isbn)

            if book:
                book['_id'] = str(book['_id'])
                return book, 200
            else:
                api.abort(404, f"No book found with ISBN {isbn} in your library")

        except Exception as e:
            if not str(e).startswith('400') and not str(e).startswith('404'):
                api.abort(500, "An unexpected error occurred")
            raise

    @api.doc('update_book')
    @api.expect(models['book_update'])
    @api.marshal_with(models['success_response'])
    @api.response(200, 'Book updated successfully')
    @api.response(400, 'Invalid input')
    @api.response(404, 'Book not found')
    @api.response(500, 'Internal server error')
    def put(self, isbn):
        """Update book information by ISBN"""
        try:
            if not validate_isbn(isbn):
                api.abort(400, "Please provide a valid ISBN-10 or ISBN-13")

            data = request.get_json()

            if not data:
                api.abort(400, "Please provide fields to update in the request body")

            if not db_service.book_exists(isbn):
                api.abort(404, f"No book found with ISBN {isbn} in your library")

            success = db_service.update_book(isbn, data)

            if success:
                updated_book = db_service.get_book_by_isbn(isbn)
                updated_book['_id'] = str(updated_book['_id'])

                return {
                    "message": "Book updated successfully",
                    "book": updated_book
                }, 200
            else:
                api.abort(500, "There was an error updating the book")

        except Exception as e:
            if not str(e).startswith('400') and not str(e).startswith('404'):
                api.abort(500, "An unexpected error occurred")
            raise

    @api.doc('delete_book')
    @api.response(200, 'Book deleted successfully')
    @api.response(400, 'Invalid ISBN format')
    @api.response(404, 'Book not found')
    @api.response(500, 'Internal server error')
    def delete(self, isbn):
        """Delete a book from library by ISBN"""
        try:
            if not validate_isbn(isbn):
                api.abort(400, "Please provide a valid ISBN-10 or ISBN-13")

            if not db_service.book_exists(isbn):
                api.abort(404, f"No book found with ISBN {isbn} in your library")

            success = db_service.delete_book(isbn)

            if success:
                return {
                    "message": "Book deleted successfully",
                    "isbn": isbn
                }, 200
            else:
                api.abort(500, "There was an error deleting the book")

        except Exception as e:
            if not str(e).startswith('400') and not str(e).startswith('404'):
                api.abort(500, "An unexpected error occurred")
            raise