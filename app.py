from flask import Flask, request, jsonify
from database import db, init_db, create_tables, User, Book, Loan
from datetime import datetime

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

@app.route('/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    """
    Retrieve a specific book with availability and loan history.
    
    Args:
        book_id: The ID of the book to retrieve
    
    Returns:
        tuple: Book details with availability stats and 200 status code, or
               error message with 404 status code if book not found
    """
    book = Book.query.get(book_id)
    if not book:
        return {"error": f"Book with ID {book_id} not found"}, 404
    
    # get loan history for the book
    total_loans = Loan.query.filter_by(book_id=book_id).count()
    active_loans = Loan.query.filter_by(book_id=book_id, return_date=None).count()
    completed_loans = Loan.query.filter(Loan.book_id==book_id, Loan.return_date.isnot(None)).count()
    
    return jsonify ({
        'book': {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn,
            'total_copies': book.total_copies,
            'available_copies': book.available_copies,
            'copies_on_loan': book.total_copies - book.available_copies
        },
        'loan_history': {
            'total_loans': total_loans,
            'active_loans': active_loans,
            'completed_loans': completed_loans,
            'availability': book.available_copies > 0
        }
    }), 200

@app.route('/books/<int:book_id>', methods=['PATCH'])
def update_book_copies(book_id):
    """
    Update the total and available copies of a book.
    
    Expected JSON payload:
        {
            "total_copies": "int" 
        }
    
    Returns:
        tuple: Success message with updated book data and 200 status code, or
               error message with 400/404 status code if validation fails
    """
    data = request.get_json()
    
    total_copies = data.get('total_copies')
    if total_copies is None:
        return {"error": "Missing total copies field"}, 400
    
    if total_copies < 0:
        return {"error": "Total copies cannot be negative"}, 400
    
    book = Book.query.get(book_id)
    if not book:
        return {"error": f"Book with ID {book_id} not found"}, 404
    
    # Calculate how many copies are currently on loan
    books_on_loan = book.total_copies - book.available_copies
    
    if total_copies < books_on_loan:
        return {"error": f"Total copies cannot be less than copies on loan ({books_on_loan})"}, 400
    
    # Update total and available copies
    book.available_copies += (total_copies - book.total_copies)
    book.total_copies = total_copies
    db.session.commit()
    
    return {"message": f"Book ID {book_id} updated", 
            "total_copies": book.total_copies, 
            "available_copies": book.available_copies}, 200

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

@app.route('/loans/<int:loan_id>', methods=['GET'])
def get_loan(loan_id):
    """
    Retrieve a specific loan by its ID.
    
    Args:
        loan_id: The ID of the loan to retrieve
    
    Returns:
        tuple: Loan details and 200 status code, or
               error message with 404 status code if loan not found
    """
    loan = Loan.query.get(loan_id)
    if not loan:
        return {"error": f"Loan with ID {loan_id} not found"}, 404
    
    user = User.query.get(loan.user_id)
    book = Book.query.get(loan.book_id)
    
    # calculate if the loan is overdue
    is_overdue = False
    days_overdue = 0
    current_fine = loan.fine
    
    if loan.return_date is None and loan.due_date < datetime.utcnow():
        is_overdue = True
        time_overdue = datetime.utcnow() - loan.due_date
        days_overdue = time_overdue.days
        current_fine = min(days_overdue * 0.50, 25.00)
        
    return jsonify ({
        'loan': {
            'id': loan.id,
            'loan_date': loan.loan_date.isoformat(),
            'due_date': loan.due_date.isoformat(),
            'return_date': loan.return_date.isoformat() if loan.return_date else None,
            'fine': loan.fine,
            'is_overdue': is_overdue,
            'is_returned': loan.return_date is not None,
            'days_overdue': days_overdue,
            'current_fine': current_fine
        },
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'phone': user.phone
        } if user else None,
        'book': {
            'id': book.id,
            'title': book.title,
            'author': book.author,
            'isbn': book.isbn
        } if book else None
    }), 200  
    
@app.route('/loans/<int:loan_id>/return', methods=['PATCH'])    
def return_book(loan_id):
    """
    Process a book return and calculate any fines for overdue books.
    
    Business Logic:
    - Fine rate: $0.50 per day overdue
    - Maximum fine: $25.00
    - Due date: 14 days from loan date
    
    Args:
        loan_id: The ID of the loan to return
    
    Returns:
        tuple: Success message with fine details and 200 status code, or
               error message with 400/404 status code if validation fails
    """
    loan = Loan.query.get(loan_id)
    if not loan:
        return {"error": f"Loan with ID {loan_id} not found"}, 404
    
    if loan.return_date is not None:
        return {"error": f"Book for Loan ID {loan_id} has already been returned"}, 400
    
    book = Book.query.get(loan.book_id)
    if not book:
        return {"error": f"Book with ID {loan.book_id} not found"}, 404
    
    # Set the return date to now
    loan.return_date = datetime.utcnow()
    
    # Calculate overdue fine if applicable
    fine = 0.0
    days_overdue = 0
    is_overdue = False
    
    if loan.return_date > loan.due_date:
        is_overdue = True
        time_overdue = loan.return_date - loan.due_date
        days_overdue = time_overdue.days
        fine = min(days_overdue * 0.50, 25.00)
        loan.fine = fine

    # Update Book's available copies
    book.available_copies += 1
    db.session.commit()
    
    response = {
        "message": f"Book ID {book.id} returned successfully",
        "loan_id": loan.id,
        "book_title": book.title,
        "return_date": loan.return_date.isoformat(),
        "due_date": loan.due_date.isoformat(),
        "is_overdue": is_overdue,
        "days_overdue": days_overdue,
        "fine": fine
    }        
    
    if is_overdue:
        response["warning"] = f"A fine of ${fine:.2f} has been applied for {days_overdue} days overdue."

    return response, 200

# Run the Flask application when the script is executed directly
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
    
    