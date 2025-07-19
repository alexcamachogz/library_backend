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

    def add_book(self, book_data):
        """
        Add a book to the collection
        Returns True if added successfully, False if it already exists
        """
        try:
            result = self.collection.insert_one(book_data)
            print(f"Book successfully added with ID: {result.inserted_id}")
            return True

        except DuplicateKeyError:
            print(f"The book with ISBN {book_data.get('isbn')} already exists in collection")
            return False
        except Exception as e:
            print(f"Error to add book into the database: {e}")
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
