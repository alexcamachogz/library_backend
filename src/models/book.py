from flask_restx import fields


def get_book_models(api):
    """
    Define Swagger models for book endpoints.

    :param api: Flask-RESTX Api instance
    :type api: Api
    :return: Dictionary containing all book models
    :rtype: dict
    """

    # Input model for adding books
    book_input = api.model('BookInput', {
        'isbn': fields.String(
            required=True,
            description='Book ISBN (10 or 13 digits)',
            example='9780439708180'
        )
    })

    # Input model for updating books
    book_update = api.model('BookUpdate', {
        'title': fields.String(description='Book title'),
        'authors': fields.List(fields.String, description='List of authors'),
        'description': fields.String(description='Book description'),
        'categories': fields.List(fields.String, description='Book categories'),
        'page_count': fields.Integer(description='Number of pages'),
        'cover_image': fields.String(description='Cover image URL'),
        'published_date': fields.String(description='Publication date'),
        'publisher': fields.String(description='Publisher name'),
        'language': fields.String(description='Book language')
    })

    # Output model for book data
    book_output = api.model('BookOutput', {
        '_id': fields.String(description='MongoDB ObjectId'),
        'isbn': fields.String(description='Book ISBN'),
        'title': fields.String(description='Book title'),
        'authors': fields.List(fields.String, description='List of authors'),
        'description': fields.String(description='Book description'),
        'categories': fields.List(fields.String, description='Book categories'),
        'page_count': fields.Integer(description='Number of pages'),
        'cover_image': fields.String(description='Cover image URL'),
        'published_date': fields.String(description='Publication date'),
        'publisher': fields.String(description='Publisher name'),
        'language': fields.String(description='Book language')
    })

    # Response models
    success_response = api.model('SuccessResponse', {
        'message': fields.String(description='Success message'),
        'book': fields.Nested(book_output, description='Book data')
    })

    error_response = api.model('ErrorResponse', {
        'error': fields.String(description='Error type'),
        'message': fields.String(description='Error message')
    })

    books_list_response = api.model('BooksListResponse', {
        'message': fields.String(description='Response message'),
        'books': fields.List(fields.Nested(book_output), description='List of books'),
        'pagination': fields.Raw(description='Pagination info')
    })

    # Search models
    search_query = api.model('SearchQuery', {
        'query': fields.String(description='General search query (searches in title, authors, description)',
                               example='harry potter'),
        'title': fields.String(description='Search specifically in book titles', example='potter'),
        'author': fields.String(description='Search specifically in authors', example='rowling'),
        'category': fields.String(description='Search specifically in categories', example='fiction'),
        'limit': fields.Integer(description='Maximum number of results (1-100)', default=50, example=20),
        'skip': fields.Integer(description='Number of results to skip for pagination', default=0, example=0)
    })

    search_response = api.model('SearchResponse', {
        'message': fields.String(description='Response message'),
        'books': fields.List(fields.Nested(book_output), description='List of matching books'),
        'search_criteria': fields.Raw(description='Search parameters used'),
        'pagination': fields.Raw(description='Pagination info')
    })

    return {
        'book_input': book_input,
        'book_update': book_update,
        'book_output': book_output,
        'success_response': success_response,
        'error_response': error_response,
        'books_list_response': books_list_response,
        'search_query': search_query,
        'search_response': search_response
    }