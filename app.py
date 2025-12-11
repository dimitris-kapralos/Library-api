from flask import Flask, request, jsonify
from database import db, init_db, create_tables, User, Book, Loan

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
    return {"message": f"Book {title} created", "id": new_book.id}, 201

@app.route('/books', methods=['GET'])
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

@app.route('/loans', methods=['POST'])
def create_loan():
    """
    Create a new loan in the database, ensuring book and user exist and copies are available.
    
    Expected JSON payload:
        {
            "user_id": "int",
            "book_id": "int"
        }
    
    Returns:
        tuple: Success message with loan ID and 201 status code, or
               error message with 400 status code if validation fails
    """
    data = request.get_json()
    
    user_id = data.get('user_id')
    book_id = data.get('book_id')
    
    # Validate required fields
    if not user_id or not book_id:
        return {'error': 'Missing required fields (user_id, book_id)'}, 400
    
    # Check if User and Book exist
    user = User.query.get(user_id)
    book = Book.query.get(book_id)
    
    if not user:
        return {'error': f'User with ID {user_id} not found'}, 404
    
    if not book:
        return {'error': f'Book with ID {book_id} not found'}, 404
        
    # Check for available copies
    if book.available_copies <= 0:
        return {'error': f'No available copies of book "{book.title}" (ID: {book_id}) for loan'}, 400
    
    # Create a new Loan object (loan_date defaults to now in the model)
    new_loan = Loan(user_id=user_id, book_id=book_id)
    
    # Update Book's available copies
    book.available_copies -= 1
    
    db.session.add(new_loan)
    db.session.commit()
    
    # Return success response with the created loan's ID
    return {"message": "Loan created", "id": new_loan.id}, 201

@app.route('/loans', methods=['GET'])
def list_loans():
    """
    Retrieve all loans from the database.
    
    Returns:
        tuple: Dictionary containing list of loans and 200 status code
    """
    loans = Loan.query.all()

    # Prepare and return the loans data
    loans_data = [{
        'id': loan.id,
        'user_id': loan.user_id,
        'book_id': loan.book_id,
        'loan_date': loan.loan_date.isoformat(),
        'due_date': loan.due_date.isoformat(),
        'return_date': loan.return_date.isoformat() if loan.return_date else None,
        'fine': loan.fine
    } for loan in loans]
    return jsonify({'loans': loans_data}), 200

# Run the Flask application when the script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
    