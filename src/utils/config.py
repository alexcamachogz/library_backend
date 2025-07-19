import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB configuration
MONGODB_URL = os.getenv('MONGODB_URL', 'mongodb://localhost:27017/')
DATABASE_NAME = 'library_inventory'
COLLECTION_NAME = 'books'

# Google Books API configuration
GOOGLE_BOOKS_BASE_URL = 'https://www.googleapis.com/books/v1/volumes'