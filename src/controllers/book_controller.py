from flask import Blueprint, request, jsonify
from src.services.google_books import GoogleBooksService
from src.services.database import DatabaseService
from src.utils.validators import validate_isbn

# Create blueprint for the books routes
book_bp = Blueprint('book', __name__)

# Init db service
db_service = DatabaseService()

@book_bp.route('/books', methods=['POST'])
def add_book():
    """
    Add a book to library by ISBN
    :return: JSON response with book info or error message
    :rtype: tuple[Response, int]
    :raises: Exception: If unexpected error occurs during processing
    """
    try:
        # Get and validate request data
        data = request.get_json()

        if not data or 'isbn' not in data:
            return jsonify({
                "error": "ISBN is required",
                "message": "Please provide an ISBN in the request body"
            }), 400
        isbn = data['isbn'].strip()

        # Validate ISBN format
        if not validate_isbn(isbn):
            return jsonify({
                "error": "Invalid ISBN format",
                "message": "Please provide a valid ISBN-10 or ISBN-13"
            }), 400

        # Check if book already exists in database
        if db_service.book_exists(isbn):
            return jsonify({
                "error": "Book already exists",
                "message": f"A book with ISBN {isbn} is already in your library."
            }), 400

        # Query Google Books API
        book_data = GoogleBooksService.get_book_by_isbn(isbn)
        if not book_data:
            return jsonify({
                "error": "Book not found",
                "message": f"No book found with ISBN {isbn} in Google Books."
            }), 400

        # Save to database
        success = db_service.add_book(book_data)
        if success:
            return jsonify({
                "message": "Book added successfully",
                "book": {
                    "isbn": book_data['isbn'],
                    "title": book_data['title'],
                    "authors": book_data['authors']
                }
            }), 201
        else:
            return jsonify({
                "error": "Failed to save book",
                "message": "There was an error saving the book to the database"
            })

    except Exception:
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        }), 500

@book_bp.route('/books', methods=['GET'])
def get_book(isbn):
    """
    Get a book from library by ISBN
    :param isbn: Book ISBN identifier
    :type isbn: str
    :return: JSON response with book data or error message
    :rtype: tuple[Response, int]
    :raises: Exception: If unexpected error occurs during retrieval
    """
    try:
        book = db_service.get_book_by_isbn(isbn)
        if book:
            # Convert ObjectId to string for JSON serialization
            book['_id'] = str(book['_id'])
            return jsonify(book), 200
        else:
            return jsonify({
                "error": "Book not found",
                "message": f"No book with ISBN {isbn} in your library."
            })
    except Exception:
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred",
        }), 500
