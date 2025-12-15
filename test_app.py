"""
Integration tests for the Library Management System.
Tests all API endpoints and business logic.
"""

import json
from database import db, User, Book, Loan


# HEALTH CHECK TESTS 

def test_health_check(client):
    """Test health check endpoint returns correct status."""
    response = client.get('/health')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert data['status'] == 'healthy'
    assert data['database'] == 'connected'
    assert 'statistics' in data
    assert 'timestamp' in data


def test_root_endpoint(client):
    """Test root endpoint returns welcome message."""
    response = client.get('/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'message' in data
    assert 'Library Management System' in data['message']


# USER ENDPOINT TESTS

def test_create_user(client):
    """Test creating a new user."""
    response = client.post('/users', json={
        'username': 'newuser',
        'email': 'newuser@example.com',
        'phone': '555-555-5555',
        'role': 'patron'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'User newuser created'
    assert 'id' in data
    
    # Verify user was created in database
    with client.application.app_context():
        user = User.query.filter_by(username='newuser').first()
        assert user is not None
        assert user.email == 'newuser@example.com'
    
def test_create_user_missing_fields(client):
    """Test creating user with missing required fields fails."""
    response = client.post('/users', json={
        'username': 'incomplete'
        # Missing email and phone
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Missing required fields' in data['error']

def test_list_users(client, sample_user):
    """Test listing all users."""
    response = client.get('/users')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'users' in data
    assert len(data['users']) >= 1
    
    # Check user structure
    user = data['users'][0]
    assert 'id' in user
    assert 'username' in user
    assert 'email' in user
    assert 'phone' in user
    assert 'role' in user
    assert 'created_at' in user

def test_sample_librarian_fixture(app, sample_librarian):
    """Verify the sample_librarian fixture inserts a librarian user into the DB."""
    with app.app_context():
        from database import User
        user = User.query.filter_by(username='librarian').first()
        assert user is not None
        assert user.email == 'librarian@example.com'
        assert user.phone == '123-456-7891'
        assert user.role == 'librarian'

def test_get_nonexistent_user(client):
    """Test getting a user that doesn't exist."""
    response = client.get('/users/99999')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data
    
# BOOK ENDPOINT TESTS 

def test_create_book(client):
    """Test creating a new book."""
    response = client.post('/books', json={
        'title': '1984',
        'author': 'George Orwell',
        'isbn': '9780451524935'
    })
    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert data['message'] == 'Book 1984 created'
    assert 'id' in data
    
    # Verify book was created with default copies
    with client.application.app_context():
        book = Book.query.filter_by(isbn='9780451524935').first()
        assert book is not None
        assert book.total_copies == 1
        assert book.available_copies == 1


def test_create_book_missing_fields(client):
    """Test creating book with missing fields fails."""
    response = client.post('/books', json={
        'title': 'Incomplete Book'
        # Missing author and isbn
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data


def test_list_books(client, sample_book):
    """Test listing all books."""
    response = client.get('/books')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'books' in data
    assert len(data['books']) >= 1
    
    # Check book structure
    book = data['books'][0]
    assert 'id' in book
    assert 'title' in book
    assert 'author' in book
    assert 'isbn' in book
    assert 'total_copies' in book
    assert 'available_copies' in book

def test_get_nonexistent_book(client):
    """Test getting a book that doesn't exist."""
    response = client.get('/books/99999')
    assert response.status_code == 404
    
    data = json.loads(response.data)
    assert 'error' in data
    
def test_multiple_books_fixture(app, multiple_books):
    """Verify multiple_books fixture inserts three books with correct attributes."""
    with app.app_context():
        db_books = Book.query.order_by(Book.id).all()
        assert len(db_books) == 3

        assert [b.title for b in db_books] == ['Book 1', 'Book 2', 'Book 3']
        assert [b.isbn for b in db_books] == ['1111111111', '2222222222', '3333333333']
        assert [b.total_copies for b in db_books] == [2, 1, 5]
        assert [b.available_copies for b in db_books] == [2, 1, 5]

def test_sample_book_fixture(app, sample_book):
    """Verify the sample_book fixture inserts a book with expected attributes."""
    with app.app_context():
        db_book = Book.query.filter_by(isbn='1234567890').first()
        assert db_book is not None
        assert db_book.title == 'Test Book'
        assert db_book.author == 'Test Author'
        assert db_book.total_copies == 3
        assert db_book.available_copies == 3
        assert sample_book.id == db_book.id

def test_update_book_negative_copies(client, sample_book):
    """Test that negative copies are rejected."""
    with client.application.app_context():
        book_id = sample_book.id
    
    response = client.patch(f'/books/{book_id}', json={
        'total_copies': -1
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data  
    
def test_update_book_copies(client, sample_book):
    """Test updating book copies."""
    with client.application.app_context():
        book_id = sample_book.id
    
    response = client.patch(f'/books/{book_id}', json={
        'total_copies': 5
    })
    
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data['total_copies'] == 5
    assert data['available_copies'] == 5
    
# LOAN ENDPOINT TESTS

def test_create_loan(client, sample_user, sample_book):
    """Test successful loan creation with valid data."""
    response = client.post('/loans', 
        json={
            'user_id': sample_user.id,
            'book_id': sample_book.id
        },
        content_type='application/json'
    )
    
    assert response.status_code == 201
    data = json.loads(response.data)
    
    # Check response structure
    assert 'message' in data
    assert data['message'] == 'Loan created successfully'
    assert 'loan' in data
    assert 'book_availability' in data
    
    # Check loan details
    loan = data['loan']
    assert loan['user_id'] == sample_user.id
    assert loan['username'] == sample_user.username
    assert loan['book_id'] == sample_book.id
    assert loan['book_title'] == sample_book.title
    assert 'loan_date' in loan
    assert 'due_date' in loan
    assert 'id' in loan
    
    # Check book availability was updated
    assert data['book_availability']['available_copies'] == 2
    assert data['book_availability']['total_copies'] == 3
    
    # Verify database was updated
    db_book = db.session.get(Book, sample_book.id)
    assert db_book.available_copies == 2
    
    # Verify loan exists in database
    db_loan = db.session.get(Loan, loan['id'])
    assert db_loan is not None
    assert db_loan.user_id == sample_user.id
    assert db_loan.book_id == sample_book.id
    assert db_loan.return_date is None
    
def test_get_loan(client, sample_loan):
    """Test getting a specific loan."""
    with client.application.app_context():
        loan_id = sample_loan.id
    
    response = client.get(f'/loans/{loan_id}')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'loan' in data
    assert 'user' in data
    assert 'book' in data
    assert data['loan']['id'] == loan_id    
    
def test_create_loan_missing_fields(client):
    """Test creating loan with missing fields fails."""
    response = client.post('/loans', json={
        'user_id': 1
        # Missing book_id
    })
    
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data    
    
def test_create_loan_nonexistent_user(client, sample_book):
    """Test creating loan with nonexistent user fails."""
    with client.application.app_context():
        book_id = sample_book.id
    
    response = client.post('/loans', json={
        'user_id': 99999,
        'book_id': book_id
    })
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'User' in data['error']
    
def test_create_loan_nonexistent_book(client, sample_user):
    """Test creating loan with nonexistent book fails."""
    with client.application.app_context():
        user_id = sample_user.id
    
    response = client.post('/loans', json={
        'user_id': user_id,
        'book_id': 99999
    })
    
    assert response.status_code == 404
    data = json.loads(response.data)
    assert 'error' in data
    assert 'Book' in data['error']
    