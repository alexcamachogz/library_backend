from flask import Flask
from flask_cors import CORS
from flask_restx import Api


def create_app():
    """
    Create and configure Flask application with Swagger documentation.

    :return: Configured Flask application
    :rtype: Flask
    """
    app = Flask(__name__)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "allow_headers": ["Content-Type"]
        }
    })

    # Configure Swagger/OpenAPI documentation
    api = Api(
        app,
        version='1.0',
        title='Library Inventory API',
        description='A simple API for managing your personal book library',
        doc='/docs/',  # Swagger UI will be available at /docs/
        prefix='/api/v1'  # All endpoints will be prefixed with /api/v1
    )

    # Register namespaces (controllers) with Swagger
    from src.controllers.book_controller import api as book_api
    api.add_namespace(book_api, path='/books')

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)