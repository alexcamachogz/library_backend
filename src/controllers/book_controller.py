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

            # Get books and total count
            books = db_service.get_all_books(limit=limit, skip=skip)
            total_count = db_service.get_total_books_count()

            return {
                "message": f"Retrieved {len(books)} books",
                "books": books,
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(books),
                    "total": total_count,
                    "has_next": skip + len(books) < total_count,
                    "has_prev": skip > 0,
                    "page": skip // limit + 1,
                    "total_pages": (total_count + limit - 1) // limit
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


@api.route('/search')
class BookSearch(Resource):
    @api.doc('search_books')
    @api.param('query', 'General search query (searches in title, authors, description)', type=str)
    @api.param('title', 'Search specifically in book titles', type=str)
    @api.param('author', 'Search specifically in authors', type=str)
    @api.param('category', 'Search specifically in categories', type=str)
    @api.param('limit', 'Maximum number of results (1-100)', type=int, default=50)
    @api.param('skip', 'Number of results to skip for pagination', type=int, default=0)
    @api.marshal_with(models['search_response'])
    @api.response(200, 'Search completed successfully')
    @api.response(400, 'Invalid search parameters')
    @api.response(500, 'Internal server error')
    def get(self):
        """Search books by title, author, category, or general query"""
        try:
            # Get search parameters
            query = request.args.get('query', '').strip()
            title = request.args.get('title', '').strip()
            author = request.args.get('author', '').strip()
            category = request.args.get('category', '').strip()
            limit = request.args.get('limit', 50, type=int)
            skip = request.args.get('skip', 0, type=int)

            # Validate pagination parameters
            if limit <= 0 or limit > 100:
                limit = 50
            if skip < 0:
                skip = 0

            # Check if at least one search parameter is provided
            if not any([query, title, author, category]):
                api.abort(400, "At least one search parameter is required (query, title, author, or category)")

            # Perform search
            books = db_service.search_books(
                query=query if query else None,
                title=title if title else None,
                author=author if author else None,
                category=category if category else None,
                limit=limit,
                skip=skip
            )

            # Get total count for this search
            total_count = db_service.search_books_count(
                query=query if query else None,
                title=title if title else None,
                author=author if author else None,
                category=category if category else None
            )

            # Build search criteria for response
            search_criteria = {}
            if query:
                search_criteria['query'] = query
            if title:
                search_criteria['title'] = title
            if author:
                search_criteria['author'] = author
            if category:
                search_criteria['category'] = category

            return {
                "message": f"Found {len(books)} books matching search criteria",
                "books": books,
                "search_criteria": search_criteria,
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(books),
                    "total": total_count,
                    "has_next": skip + len(books) < total_count,
                    "has_prev": skip > 0,
                    "page": skip // limit + 1,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }, 200

        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")


@api.route('/authors/<string:author>')
@api.param('author', 'Author name to search for')
class BooksByAuthor(Resource):
    @api.doc('get_books_by_author')
    @api.param('limit', 'Maximum number of results (1-100)', type=int, default=50)
    @api.param('skip', 'Number of results to skip for pagination', type=int, default=0)
    @api.marshal_with(models['search_response'])
    @api.response(200, 'Books retrieved successfully')
    @api.response(400, 'Invalid parameters')
    @api.response(500, 'Internal server error')
    def get(self, author):
        """Get all books by a specific author"""
        try:
            limit = request.args.get('limit', 50, type=int)
            skip = request.args.get('skip', 0, type=int)

            # Validate pagination parameters
            if limit <= 0 or limit > 100:
                limit = 50
            if skip < 0:
                skip = 0

            books = db_service.get_books_by_author(author, limit=limit, skip=skip)
            total_count = db_service.get_books_by_author_count(author)

            return {
                "message": f"Found {len(books)} books by author '{author}'",
                "books": books,
                "search_criteria": {"author": author},
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(books),
                    "total": total_count,
                    "has_next": skip + len(books) < total_count,
                    "has_prev": skip > 0,
                    "page": skip // limit + 1,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }, 200

        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")


@api.route('/categories/<string:category>')
@api.param('category', 'Category name to search for')
class BooksByCategory(Resource):
    @api.doc('get_books_by_category')
    @api.param('limit', 'Maximum number of results (1-100)', type=int, default=50)
    @api.param('skip', 'Number of results to skip for pagination', type=int, default=0)
    @api.marshal_with(models['search_response'])
    @api.response(200, 'Books retrieved successfully')
    @api.response(400, 'Invalid parameters')
    @api.response(500, 'Internal server error')
    def get(self, category):
        """Get all books in a specific category"""
        try:
            limit = request.args.get('limit', 50, type=int)
            skip = request.args.get('skip', 0, type=int)

            # Validate pagination parameters
            if limit <= 0 or limit > 100:
                limit = 50
            if skip < 0:
                skip = 0

            books = db_service.get_books_by_category(category, limit=limit, skip=skip)
            total_count = db_service.get_books_by_category_count(category)

            return {
                "message": f"Found {len(books)} books in category '{category}'",
                "books": books,
                "search_criteria": {"category": category},
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(books),
                    "total": total_count,
                    "has_next": skip + len(books) < total_count,
                    "has_prev": skip > 0,
                    "page": skip // limit + 1,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }, 200

        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")


@api.route('/<string:isbn>/status')
@api.param('isbn', 'Book ISBN identifier')
class BookStatus(Resource):
    @api.doc('update_reading_status')
    @api.expect(models['status_update'])
    @api.marshal_with(models['status_response'])
    @api.response(200, 'Reading status updated successfully')
    @api.response(400, 'Invalid input')
    @api.response(404, 'Book not found')
    @api.response(500, 'Internal server error')
    def put(self, isbn):
        """Update reading status of a book"""
        try:
            if not validate_isbn(isbn):
                api.abort(400, "Please provide a valid ISBN-10 or ISBN-13")

            data = request.get_json()

            if not data or 'reading_status' not in data:
                api.abort(400, "Reading status is required")

            status = data['reading_status']

            if status not in ['read', 'unread', 'in_progress']:
                api.abort(400, "Reading status must be 'read', 'unread', or 'in_progress'")

            if not db_service.book_exists(isbn):
                api.abort(404, f"No book found with ISBN {isbn} in your library")

            success = db_service.update_reading_status(isbn, status)

            if success:
                return {
                    "message": f"Reading status updated to '{status}'",
                    "isbn": isbn,
                    "reading_status": status
                }, 200
            else:
                api.abort(500, "There was an error updating the reading status")

        except Exception as e:
            if not str(e).startswith('400') and not str(e).startswith('404'):
                api.abort(500, "An unexpected error occurred")
            raise


@api.route('/status/<string:status>')
@api.param('status', 'Reading status to filter by', enum=['read', 'unread', 'in_progress'])
class BooksByStatus(Resource):
    @api.doc('get_books_by_status')
    @api.param('limit', 'Maximum number of results (1-100)', type=int, default=50)
    @api.param('skip', 'Number of results to skip for pagination', type=int, default=0)
    @api.marshal_with(models['search_response'])
    @api.response(200, 'Books retrieved successfully')
    @api.response(400, 'Invalid status parameter')
    @api.response(500, 'Internal server error')
    def get(self, status):
        """Get all books by reading status"""
        try:
            if status not in ['read', 'unread', 'in_progress']:
                api.abort(400, "Status must be 'read', 'unread', or 'in_progress'")

            limit = request.args.get('limit', 50, type=int)
            skip = request.args.get('skip', 0, type=int)

            # Validate pagination parameters
            if limit <= 0 or limit > 100:
                limit = 50
            if skip < 0:
                skip = 0

            books = db_service.get_books_by_status(status, limit=limit, skip=skip)
            total_count = db_service.get_books_by_status_count(status)

            return {
                "message": f"Found {len(books)} {status} books",
                "books": books,
                "search_criteria": {"reading_status": status},
                "pagination": {
                    "limit": limit,
                    "skip": skip,
                    "count": len(books),
                    "total": total_count,
                    "has_next": skip + len(books) < total_count,
                    "has_prev": skip > 0,
                    "page": skip // limit + 1,
                    "total_pages": (total_count + limit - 1) // limit
                }
            }, 200

        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")


@api.route('/statistics')
class ReadingStatistics(Resource):
    @api.doc('get_reading_statistics')
    @api.response(200, 'Statistics retrieved successfully')
    @api.response(500, 'Internal server error')
    def get(self):
        """Get reading statistics (read vs unread vs in_progress books)"""
        try:
            stats = db_service.get_reading_statistics()

            return {
                "message": "Reading statistics retrieved successfully",
                "statistics": stats
            }, 200

        except Exception as e:
            api.abort(500, f"An unexpected error occurred: {str(e)}")

@api.route('/manual')
class ManualBook(Resource):
    @api.doc('add_manual_book')
    @api.expect(models['book_manual_input'])
    @api.marshal_with(models['success_response'])
    @api.response(201, 'Book added successfully')
    @api.response(400, 'Invalid input')
    @api.response(409, 'Book already exists')
    @api.response(500, 'Internal server error')
    def post(self):
        """Add a book manually with all details"""
        try:
            data = request.get_json()

            if not data:
                api.abort(400, "Book data is required")

            # Required fields validation
            required_fields = ['isbn', 'title', 'authors']
            for field in required_fields:
                if field not in data or not data[field]:
                    api.abort(400, f"{field.title()} is required")

            isbn = data['isbn'].strip()

            # Validate ISBN format
            if not validate_isbn(isbn):
                api.abort(400, "Please provide a valid ISBN-10 or ISBN-13")

            # Check if book already exists
            if db_service.book_exists(isbn):
                api.abort(409, f"A book with ISBN {isbn} is already in your library")

            # Prepare book data
            book_data = {
                'isbn': isbn,
                'title': data['title'].strip(),
                'authors': data['authors'] if isinstance(data['authors'], list) else [data['authors']],
                'description': data.get('description', ''),
                'categories': data.get('categories', []),
                'page_count': data.get('page_count'),
                'cover_image': data.get('cover_image', ''),
                'published_date': data.get('published_date', ''),
                'publisher': data.get('publisher', ''),
                'language': data.get('language', 'en'),
                'reading_status': data.get('reading_status', 'unread')
            }

            # Validate reading status
            if book_data['reading_status'] not in ['read', 'unread', 'in_progress']:
                book_data['reading_status'] = 'unread'

            # Ensure page_count is integer or None
            if book_data['page_count'] is not None:
                try:
                    book_data['page_count'] = int(book_data['page_count'])
                except (ValueError, TypeError):
                    book_data['page_count'] = None

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
            if not str(e).startswith('400') and not str(e).startswith('409'):
                api.abort(500, f"An unexpected error occurred: {str(e)}")
            raise