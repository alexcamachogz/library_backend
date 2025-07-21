from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError, ConnectionFailure
from src.utils.config import MONGODB_URL, DATABASE_NAME, COLLECTION_NAME

class DatabaseService:

    def __init__(self):
        """
        Initialize MongoDB connection.
        :raises ConnectionFailure: If cannot connect to MongoDB
        :raises Exception: If unexpected error during initialization
        """
        try:
            print(f"Connecting to MongoDB: {MONGODB_URL}")
            print(f"Database: {DATABASE_NAME}, Collection: {COLLECTION_NAME}")

            self.client = MongoClient(MONGODB_URL)
            self.db = self.client[DATABASE_NAME]
            self.collection = self.db[COLLECTION_NAME]

            # Test connection
            self.client.admin.command('ping')
            print("MongoDB connection established successfully")

        except ConnectionFailure as e:
            print(f"Error connecting to MongoDB: {e}")
            raise
        except Exception as e:
            print(f"Unexpected error initializing database: {e}")
            raise

    # Create
    def add_book(self, book_data):
        """
        Add a book to the MongoDB collection.

        :param book_data: Dictionary containing book information
        :type book_data: dict
        :return: True if book was added successfully, False if already exists
        :rtype: bool
        :raises Exception: If database operation fails
        """
        try:
            if 'reading_status' not in book_data:
                book_data['reading_status'] = 'unread'

            result = self.collection.insert_one(book_data)
            print(f"Book successfully added with ID: {result.inserted_id}")
            return True

        except DuplicateKeyError:
            print(f"The book with ISBN {book_data.get('isbn')} already exists in collection")
            return False
        except Exception as e:
            print(f"Error to add book into the database: {e}")
            raise

    # Read
    def get_all_books(self, limit=50, skip=0):
        """
        Get all books with pagination.

        :param limit: Maximum number of books to return
        :type limit: int
        :param skip: Number of books to skip
        :type skip: int
        :return: List of books
        :rtype: list
        :raises Exception: If database operation fails
        """
        try:
            books = list(self.collection.find().skip(skip).limit(limit))

            # Convert ObjectId to string for JSON serialization
            for book in books:
                book['_id'] = str(book['_id'])

            print(f"Retrieved {len(books)} books from database")
            return books

        except Exception as e:
            print(f"Error retrieving books: {e}")
            raise

    # Update
    def update_book(self, isbn, updated_data):
        """
        Update book information by ISBN.

        :param isbn: Book ISBN identifier
        :type isbn: str
        :param updated_data: Dictionary with fields to update
        :type updated_data: dict
        :return: True if book was updated, False if not found
        :rtype: bool
        :raises Exception: If database operation fails
        """
        try:
            # Remove ISBN from updated_data to prevent changing the unique key
            if 'isbn' in updated_data:
                del updated_data['isbn']

            result = self.collection.update_one(
                {"isbn": isbn},
                {"$set": updated_data}
            )

            if result.matched_count > 0:
                print(f"Book with ISBN {isbn} updated successfully")
                return True
            else:
                print(f"No book found with ISBN {isbn}")
                return False

        except Exception as e:
            print(f"Error updating book: {e}")
            raise

    # Delete
    def delete_book(self, isbn):
        """
        Delete a book by ISBN.

        :param isbn: Book ISBN identifier
        :type isbn: str
        :return: True if book was deleted, False if not found
        :rtype: bool
        :raises Exception: If database operation fails
        """
        try:
            result = self.collection.delete_one({"isbn": isbn})

            if result.deleted_count > 0:
                print(f"Book with ISBN {isbn} deleted successfully")
                return True
            else:
                print(f"No book found with ISBN {isbn}")
                return False

        except Exception as e:
            print(f"Error deleting book: {e}")
            raise

    def book_exists(self, isbn):
        """
        Verify if the book exists in the collection
        """
        try:
            count = self.collection.count_documents({"isbn": isbn})
            return count > 0
        except Exception as e:
            print(f"Error checking existence of book: {e}")
            raise

    def get_book_by_isbn(self, isbn):
        """
        Get book by ISBN
        """
        try:
            book = self.collection.find_one({"isbn": isbn})
            return book
        except Exception as e:
            print(f"Error getting book: {e}")

    def close_connection(self):
        """
        Close the database connection
        """
        if self.client:
            self.client.close()
            print("Connection to MongoDB closed")

    def search_books(self, query=None, title=None, author=None, category=None, limit=50, skip=0):
        """
        Search books by different criteria.

        :param query: General search query (searches in title, authors, description)
        :type query: str
        :param title: Search specifically in title
        :type title: str
        :param author: Search specifically in authors
        :type author: str
        :param category: Search specifically in categories
        :type category: str
        :param limit: Maximum number of books to return
        :type limit: int
        :param skip: Number of books to skip
        :type skip: int
        :return: List of matching books
        :rtype: list
        :raises Exception: If database operation fails
        """
        try:
            # Build search filters
            filters = {}

            if query:
                # General search using $or operator for multiple fields
                filters['$or'] = [
                    {'title': {'$regex': query, '$options': 'i'}},
                    {'authors': {'$regex': query, '$options': 'i'}},
                    {'description': {'$regex': query, '$options': 'i'}}
                ]

            if title:
                filters['title'] = {'$regex': title, '$options': 'i'}

            if author:
                filters['authors'] = {'$regex': author, '$options': 'i'}

            if category:
                filters['categories'] = {'$regex': category, '$options': 'i'}

            # If no search criteria provided, return empty list
            if not filters:
                return []

            # Execute search with pagination
            books = list(
                self.collection.find(filters)
                .skip(skip)
                .limit(limit)
            )

            # Convert ObjectId to string for JSON serialization
            for book in books:
                book['_id'] = str(book['_id'])

            print(f"Found {len(books)} books matching search criteria")
            return books

        except Exception as e:
            print(f"Error searching books: {e}")
            raise

    def get_books_by_author(self, author, limit=50, skip=0):
        """
        Get books by specific author.

        :param author: Author name to search for
        :type author: str
        :param limit: Maximum number of books to return
        :type limit: int
        :param skip: Number of books to skip
        :type skip: int
        :return: List of books by the author
        :rtype: list
        :raises Exception: If database operation fails
        """
        try:
            books = list(
                self.collection.find({
                    'authors': {'$regex': author, '$options': 'i'}
                })
                .skip(skip)
                .limit(limit)
            )

            for book in books:
                book['_id'] = str(book['_id'])

            print(f"Found {len(books)} books by author '{author}'")
            return books

        except Exception as e:
            print(f"Error getting books by author: {e}")
            raise

    def get_books_by_category(self, category, limit=50, skip=0):
        """
        Get books by specific category.

        :param category: Category to search for
        :type category: str
        :param limit: Maximum number of books to return
        :type limit: int
        :param skip: Number of books to skip
        :type skip: int
        :return: List of books in the category
        :rtype: list
        :raises Exception: If database operation fails
        """
        try:
            books = list(
                self.collection.find({
                    'categories': {'$regex': category, '$options': 'i'}
                })
                .skip(skip)
                .limit(limit)
            )

            for book in books:
                book['_id'] = str(book['_id'])

            print(f"Found {len(books)} books in category '{category}'")
            return books

        except Exception as e:
            print(f"Error getting books by category: {e}")
            raise

    def update_reading_status(self, isbn, status):
        """
        Update reading status of a book.

        :param isbn: Book ISBN identifier
        :type isbn: str
        :param status: New reading status ('read' or 'unread')
        :type status: str
        :return: True if status was updated, False if book not found
        :rtype: bool
        :raises Exception: If database operation fails
        """
        try:
            # Validate status
            if status not in ['read', 'unread']:
                raise ValueError("Status must be 'read' or 'unread'")

            result = self.collection.update_one(
                {"isbn": isbn},
                {"$set": {"reading_status": status}}
            )

            if result.matched_count > 0:
                print(f"Reading status for ISBN {isbn} updated to '{status}'")
                return True
            else:
                print(f"No book found with ISBN {isbn}")
                return False

        except Exception as e:
            print(f"Error updating reading status: {e}")
            raise

    def get_books_by_status(self, status, limit=50, skip=0):
        """
        Get books by reading status.

        :param status: Reading status to filter by ('read' or 'unread')
        :type status: str
        :param limit: Maximum number of books to return
        :type limit: int
        :param skip: Number of books to skip
        :type skip: int
        :return: List of books with the specified status
        :rtype: list
        :raises Exception: If database operation fails
        """
        try:
            if status not in ['read', 'unread']:
                raise ValueError("Status must be 'read' or 'unread'")

            books = list(
                self.collection.find({"reading_status": status})
                .skip(skip)
                .limit(limit)
            )

            # Convert ObjectId to string for JSON serialization
            for book in books:
                book['_id'] = str(book['_id'])

            print(f"Found {len(books)} books with status '{status}'")
            return books

        except Exception as e:
            print(f"Error getting books by status: {e}")
            raise

    def get_reading_statistics(self):
        """
        Get reading statistics (count of read vs unread books).

        :return: Dictionary with reading statistics
        :rtype: dict
        :raises Exception: If database operation fails
        """
        try:
            # Count books by status
            read_count = self.collection.count_documents({"reading_status": "read"})
            unread_count = self.collection.count_documents({"reading_status": "unread"})
            total_count = self.collection.count_documents({})

            # Handle books without reading_status (existing books)
            no_status_count = total_count - read_count - unread_count

            stats = {
                "total_books": total_count,
                "read": read_count,
                "unread": unread_count + no_status_count,  # Consider books without status as unread
                "reading_percentage": round((read_count / total_count * 100), 2) if total_count > 0 else 0
            }

            print(f"Reading statistics: {stats}")
            return stats

        except Exception as e:
            print(f"Error getting reading statistics: {e}")
            raise