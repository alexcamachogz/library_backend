from flask import Blueprint, request, jsonify

# Create blueprint for the books routes
book_bp = Blueprint('book', __name__)

@book_bp.route('/books', methods=['POST'])
def add_book():
    try:
        # Get ISBN from the request
        data = request.get_json()
        isbn = data.get('isbn')

        # TODO: Validate ISBN
        # TODO: Shear Google Books
        # TODO: Save in MongoDB

        return jsonify({"message": "Functionality in development"}), 200

    except Exception as e:
        return jsonify({"message": str(e)}), 400
