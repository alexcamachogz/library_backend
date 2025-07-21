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

    return {
        'book_input': book_input,
        'book_update': book_update,
        'book_output': book_output,
        'success_response': success_response,
        'error_response': error_response,
        'books_list_response': books_list_response
    }