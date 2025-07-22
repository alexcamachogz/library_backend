# Agregar este modelo en tu models/book.py

from flask_restx import fields


def get_book_models(api):
    """
    Get Swagger models for book operations.

    :param api: Flask-RESTX API instance
    :type api: flask_restx.Api
    :return: Dictionary of models
    :rtype: dict
    """

    # Input model for ISBN-based book addition
    book_input = api.model('BookInput', {
        'isbn': fields.String(required=True, description='Book ISBN', example='9780439708180')
    })

    # NEW: Manual book input model
    book_manual_input = api.model('BookManualInput', {
        'isbn': fields.String(required=True, description='Book ISBN', example='9780439708180'),
        'title': fields.String(required=True, description='Book title',
                               example='Harry Potter and the Philosopher\'s Stone'),
        'authors': fields.List(fields.String, required=True, description='List of authors', example=['J.K. Rowling']),
        'description': fields.String(description='Book description',
                                     example='Harry Potter has never even heard of Hogwarts when the letters start dropping on the doormat at number four, Privet Drive...'),
        'categories': fields.List(fields.String, description='List of categories',
                                  example=['Fiction', 'Fantasy', 'Young Adult']),
        'page_count': fields.Integer(description='Number of pages', example=223),
        'cover_image': fields.String(description='URL of book cover image', example='https://example.com/cover.jpg'),
        'published_date': fields.String(description='Publication date (YYYY-MM-DD)', example='1997-06-26'),
        'publisher': fields.String(description='Publisher name', example='Bloomsbury'),
        'language': fields.String(description='Book language code', example='en'),
        'reading_status': fields.String(description='Reading status', enum=['read', 'unread'], example='unread')
    })

    # Book output model
    book_output = api.model('BookOutput', {
        '_id': fields.String(description='Book ID'),
        'isbn': fields.String(description='Book ISBN'),
        'title': fields.String(description='Book title'),
        'authors': fields.List(fields.String, description='List of authors'),
        'description': fields.String(description='Book description'),
        'categories': fields.List(fields.String, description='List of categories'),
        'page_count': fields.Integer(description='Number of pages'),
        'cover_image': fields.String(description='URL of book cover image'),
        'published_date': fields.String(description='Publication date'),
        'publisher': fields.String(description='Publisher'),
        'language': fields.String(description='Book language'),
        'reading_status': fields.String(description='Reading status')
    })

    # Book update model
    book_update = api.model('BookUpdate', {
        'title': fields.String(description='Book title'),
        'authors': fields.List(fields.String, description='List of authors'),
        'description': fields.String(description='Book description'),
        'categories': fields.List(fields.String, description='List of categories'),
        'page_count': fields.Integer(description='Number of pages'),
        'cover_image': fields.String(description='URL of book cover image'),
        'published_date': fields.String(description='Publication date'),
        'publisher': fields.String(description='Publisher'),
        'language': fields.String(description='Book language'),
        'reading_status': fields.String(description='Reading status', enum=['read', 'unread'])
    })

    # Status update model
    status_update = api.model('StatusUpdate', {
        'reading_status': fields.String(required=True, description='Reading status', enum=['read', 'unread'])
    })

    # Success response model
    success_response = api.model('SuccessResponse', {
        'message': fields.String(description='Success message'),
        'book': fields.Nested(book_output, description='Book data')
    })

    # Status response model
    status_response = api.model('StatusResponse', {
        'message': fields.String(description='Success message'),
        'isbn': fields.String(description='Book ISBN'),
        'reading_status': fields.String(description='Updated reading status')
    })

    # Pagination model
    pagination_model = api.model('Pagination', {
        'limit': fields.Integer(description='Number of items per page'),
        'skip': fields.Integer(description='Number of items skipped'),
        'count': fields.Integer(description='Number of items in current page'),
        'total': fields.Integer(description='Total number of items'),
        'has_next': fields.Boolean(description='Whether there are more pages'),
        'has_prev': fields.Boolean(description='Whether there are previous pages'),
        'page': fields.Integer(description='Current page number'),
        'total_pages': fields.Integer(description='Total number of pages')
    })

    # Search criteria model
    search_criteria = api.model('SearchCriteria', {
        'query': fields.String(description='General search query'),
        'title': fields.String(description='Title search'),
        'author': fields.String(description='Author search'),
        'category': fields.String(description='Category search'),
        'reading_status': fields.String(description='Reading status filter')
    })

    # Books list response model
    books_list_response = api.model('BooksListResponse', {
        'message': fields.String(description='Response message'),
        'books': fields.List(fields.Nested(book_output), description='List of books'),
        'pagination': fields.Nested(pagination_model, description='Pagination information')
    })

    # Search response model
    search_response = api.model('SearchResponse', {
        'message': fields.String(description='Response message'),
        'books': fields.List(fields.Nested(book_output), description='List of books'),
        'search_criteria': fields.Nested(search_criteria, description='Search criteria used'),
        'pagination': fields.Nested(pagination_model, description='Pagination information')
    })

    return {
        'book_input': book_input,
        'book_manual_input': book_manual_input,
        'book_output': book_output,
        'book_update': book_update,
        'status_update': status_update,
        'success_response': success_response,
        'status_response': status_response,
        'pagination_model': pagination_model,
        'search_criteria': search_criteria,
        'books_list_response': books_list_response,
        'search_response': search_response
    }