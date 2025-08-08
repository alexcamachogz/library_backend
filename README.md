# Library Inventory API 📚

A comprehensive REST API for managing your personal book library, built with Flask and MongoDB. This API allows you to track books, manage reading status, search through your collection, and organize books by categories.

## ✨ Features

- **Book Management**: Add, update, delete, and retrieve books
- **Google Books Integration**: Automatically fetch book details using ISBN
- **Manual Book Entry**: Add books manually with custom details
- **Advanced Search**: Search books by title, author, category, or general query
- **Category Filtering**: Filter books by single or multiple categories
- **Reading Status Tracking**: Track books as read, unread, or in progress
- **Statistics**: Get reading statistics and progress analytics
- **Pagination**: Efficient pagination for large collections
- **Swagger Documentation**: Interactive API documentation available at `/docs/`

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MongoDB Atlas account or local MongoDB installation
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd library_inventory
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file in the root directory:
   ```env
   MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority
   DATABASE_NAME=library_inventory
   COLLECTION_NAME=books
   ```

5. **Run the application**
   ```bash
   python src/app.py
   ```

The API will be available at `http://localhost:5001`

### Docker Support

If you prefer using Docker, you can build and run the application with:

```bash
docker build -t library-inventory .
docker run -p 5001:5001 --env-file .env library-inventory
```

## 📖 API Documentation

The API provides comprehensive Swagger documentation available at:
- **Interactive Documentation**: `http://localhost:5001/docs/`
- **API Base URL**: `http://localhost:5001/api/v1`

### Authentication

Currently, the API doesn't require authentication. All endpoints are publicly accessible.

## 🔗 API Endpoints

### Books Management

#### Get All Books
```http
GET /api/v1/books/
```
**Query Parameters:**
- `limit` (int, optional): Maximum number of books to return (1-100, default: 50)
- `skip` (int, optional): Number of books to skip for pagination (default: 0)

#### Add Book by ISBN
```http
POST /api/v1/books/
Content-Type: application/json

{
  "isbn": "9780123456789"
}
```

#### Add Book Manually
```http
POST /api/v1/books/manual
Content-Type: application/json

{
  "isbn": "9780123456789",
  "title": "Book Title",
  "authors": ["Author Name"],
  "description": "Book description",
  "categories": ["Fiction", "Drama"],
  "page_count": 300,
  "publisher": "Publisher Name",
  "published_date": "2023-01-15",
  "language": "en",
  "reading_status": "unread"
}
```

#### Get Book by ISBN
```http
GET /api/v1/books/{isbn}
```

#### Update Book
```http
PUT /api/v1/books/{isbn}
Content-Type: application/json

{
  "title": "Updated Title",
  "reading_status": "read"
}
```

#### Delete Book
```http
DELETE /api/v1/books/{isbn}
```

### Search and Filtering

#### Search Books
```http
GET /api/v1/books/search
```
**Query Parameters:**
- `query` (string): General search across title, authors, and description
- `title` (string): Search specifically in book titles
- `author` (string): Search specifically in authors
- `category` (string): Search specifically in categories
- `limit` (int): Maximum results (default: 50)
- `skip` (int): Pagination offset (default: 0)

#### Filter by Multiple Categories
```http
GET /api/v1/books/filter/categories?categories=Fiction,Fantasy,Drama
```
**Query Parameters:**
- `categories` (string, required): Comma-separated list of categories
- `limit` (int): Maximum results (default: 50)
- `skip` (int): Pagination offset (default: 0)

#### Get Books by Author
```http
GET /api/v1/books/authors/{author_name}
```

#### Get Books by Category
```http
GET /api/v1/books/categories/{category_name}
```

#### Get Books by Reading Status
```http
GET /api/v1/books/status/{status}
```
**Valid status values:** `read`, `unread`, `in_progress`

### Reading Status Management

#### Update Reading Status
```http
PUT /api/v1/books/{isbn}/status
Content-Type: application/json

{
  "reading_status": "read"
}
```

### Statistics

#### Get Reading Statistics
```http
GET /api/v1/books/statistics
```

**Response Example:**
```json
{
  "message": "Reading statistics retrieved successfully",
  "statistics": {
    "total_books": 150,
    "read": 45,
    "unread": 90,
    "in_progress": 15,
    "reading_percentage": 30.0,
    "progress_percentage": 10.0
  }
}
```

## 📊 Response Format

All API responses follow a consistent format:

### Success Response
```json
{
  "message": "Success message",
  "books": [...],
  "pagination": {
    "limit": 50,
    "skip": 0,
    "count": 25,
    "total": 150,
    "has_next": true,
    "has_prev": false,
    "page": 1,
    "total_pages": 3
  }
}
```

### Error Response
```json
{
  "message": "Error description"
}
```

## 🗃️ Data Models

### Book Model
```json
{
  "_id": "unique_mongodb_id",
  "isbn": "9780123456789",
  "title": "Book Title",
  "authors": ["Author Name"],
  "description": "Book description",
  "categories": ["Fiction", "Drama"],
  "page_count": 300,
  "cover_image": "https://example.com/cover.jpg",
  "published_date": "2023-01-15",
  "publisher": "Publisher Name",
  "language": "en",
  "reading_status": "unread"
}
```

### Reading Status Values
- `read`: Book has been completed
- `unread`: Book hasn't been started (default)
- `in_progress`: Book is currently being read

## 🔧 Configuration

### Environment Variables

Create a `.env` file or set these environment variables:

| Variable | Description | Default |
|----------|-------------|---------|
| `MONGODB_URL` | MongoDB connection string | Required |
| `DATABASE_NAME` | MongoDB database name | `library_inventory` |
| `COLLECTION_NAME` | MongoDB collection name | `books` |

### Configuration Files

The application uses configuration files located in `src/utils/config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv('MONGODB_URL')
DATABASE_NAME = os.getenv('DATABASE_NAME', 'library_inventory')
COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'books')
```

## 🚀 Deployment

### Heroku Deployment

The application is ready for Heroku deployment with the included `Procfile`:

1. **Create Heroku app**
   ```bash
   heroku create your-app-name
   ```

2. **Set environment variables**
   ```bash
   heroku config:set MONGODB_URL="your_mongodb_connection_string"
   heroku config:set DATABASE_NAME="library_inventory"
   heroku config:set COLLECTION_NAME="books"
   ```

3. **Deploy**
   ```bash
   git push heroku main
   ```

### Other Platforms

The application can be deployed to any platform that supports Python applications:
- **Render**: Supports direct deployment from Git
- **Railway**: Easy deployment with Git integration
- **PythonAnywhere**: Traditional hosting platform
- **AWS EC2**: Full control with custom setup

## 🧪 Testing

### Manual Testing

You can test the API using curl, Postman, or any HTTP client:

```bash
# Add a book
curl -X POST "http://localhost:5001/api/v1/books/" \
  -H "Content-Type: application/json" \
  -d '{"isbn": "9780439708180"}'

# Search books
curl -X GET "http://localhost:5001/api/v1/books/search?query=Harry Potter"

# Filter by categories
curl -X GET "http://localhost:5001/api/v1/books/filter/categories?categories=Fiction,Fantasy"
```

### Using Swagger UI

Visit `http://localhost:5001/docs/` to interact with the API using the built-in Swagger interface.

## 🏗️ Project Structure

```
library_inventory/
├── src/
│   ├── __init__.py
│   ├── app.py                 # Flask application entry point
│   ├── controllers/
│   │   ├── __init__.py
│   │   └── book_controller.py # API endpoints and routes
│   ├── models/
│   │   ├── __init__.py
│   │   └── book.py           # Swagger models definition
│   ├── services/
│   │   ├── __init__.py
│   │   ├── database.py       # MongoDB operations
│   │   └── google_books.py   # Google Books API integration
│   └── utils/
│       ├── __init__.py
│       ├── config.py         # Configuration management
│       └── validators.py     # Input validation utilities
├── requirements.txt          # Python dependencies
├── Procfile                 # Heroku deployment configuration
├── .env                     # Environment variables (create this)
└── README.md               # This file
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

### Development Guidelines

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Include error handling for all database operations
- Update the README when adding new features
- Test all endpoints before submitting

## 📝 License

This project is licensed under the MIT License. See the LICENSE file for details.

## 🐛 Known Issues

- Currently, the API doesn't support bulk operations for adding multiple books
- Image upload functionality is not yet implemented
- No user authentication or authorization system

## 📞 Support

If you encounter any issues or have questions:
1. Check the [API documentation](http://localhost:5001/docs/)
2. Review existing GitHub issues
3. Create a new issue with detailed information

## 🙏 Acknowledgments

- **Google Books API** for providing book metadata
- **Flask-RESTX** for API documentation and validation
- **MongoDB** for reliable data storage
- **All contributors** who help improve this project

---

Made with ❤️ for book lovers everywhere 📖
