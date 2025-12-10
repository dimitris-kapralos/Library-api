from flask import Flask, request, jsonify
from database import db, init_db, create_tables, User, Book

# Initialize the Flask application and database
app = Flask(__name__)
init_db(app)
create_tables(app)


@app.route('/')
def hello():
    """
    Root endpoint that returns a simple greeting message.
    
    Returns:
        dict: A welcome message
    """
    return {'message': 'Hello, World!'}


@app.route('/users', methods=['POST'])
def create_user():
    """
    Create a new user in the database.
    
    Expected JSON payload:
        {
            "username": "string",
            "email": "string",
            "phone": "string",
            "role": "string" (optional, defaults to 'patron')
        }
    
    Returns:
        tuple: Success message with user ID and 201 status code, or
               error message with 400 status code if validation fails
    """
    data = request.get_json()
    
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    role = data.get('role', 'patron')
    
    
    # Validate that all required fields are present
    if not username or not email or not phone:
        return {'error': 'Missing required fields'}, 400
    
    # Create a new User object and add it to the database
    new_user = User(username=username, email=email, phone=phone, role=role)
    db.session.add(new_user)
    db.session.commit()
    
    # Return success response with the created user's ID
    return {"message": f"User {username} created", "id": new_user.id}, 201


@app.route('/users', methods=['GET'])
def list_users():
    """
    Retrieve all users from the database.
    
    Returns:
        tuple: Dictionary containing list of users and 200 status code
    """
    users = User.query.all()

    # Prepare and return the users data
    users_data = [{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'phone': user.phone,
        'role': user.role,
        'created_at': user.created_at.isoformat()
    } for user in users]
    return jsonify({'users': users_data}), 200

@app.route('/books', methods=['POST'])
def create_book():
    """
    Create a new book in the database.
    
    Expected JSON payload:
        {
            "title": "string",
            "author": "string",
            "isbn": "string"
        }
    
    Returns:
        tuple: Success message with book ID and 201 status code, or
               error message with 400 status code if validation fails
    """
    data = request.get_json()
    
    title = data.get('title')
    author = data.get('author')
    isbn = data.get('isbn')
    
    # Validate that all required fields are present
    if not title or not author or not isbn:
        return {'error': 'Missing required fields'}, 400
    
    # Create a new Book object and add it to the database
    new_book = Book(title=title, author=author, isbn=isbn)
    db.session.add(new_book)
    db.session.commit()
    
    # Return success response with the created book's ID
    return {"message": f"Book {title} created", "id": new_book.id}, 

@app('/books', methods=['GET'])
def list_books():
    """
    Retrieve all books from the database.
    
    Returns:
        tuple: Dictionary containing list of books and 200 status code
    """
    books = Book.query.all()

    # Prepare and return the books data
    books_data = [{
        'id': book.id,
        'title': book.title,
        'author': book.author,
        'isbn': book.isbn,
        'total_copies': book.total_copies,
        'available_copies': book.available_copies
    } for book in books]
    return jsonify({'books': books_data}), 200


# Run the Flask application when the script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
    