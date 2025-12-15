"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
from app import app as flask_app
from database import db, User, Book, Loan
from datetime import datetime, timedelta

@pytest.fixture
def app():
    """
    Create and configure a Flask application instance for testing.
    Uses in-memory SQLite database.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    flask_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    with flask_app.app_context():
        db.create_all()
        yield flask_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """
    Create a test client for making HTTP requests.
    """
    return app.test_client()


@pytest.fixture
def runner(app):
    """
    Create a test runner for CLI commands.
    """
    return app.test_cli_runner()

@pytest.fixture
def sample_user(app):
    """
    Create a sample user in the database.
    
    Returns:
        User: A user object with username='testuser'
    """
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            phone='123-456-7890',
            role='patron'
        )
        db.session.add(user)
        db.session.commit()
        db.session.refresh(user)
        db.session.expunge(user)        
        return user


@pytest.fixture
def sample_librarian(app):
    """
    Create a sample librarian user in the database.
    
    Returns:
        User: A user object with role='librarian'
    """
    with app.app_context():
        user = User(
            username='librarian',
            email='librarian@example.com',
            phone='123-456-7891',
            role='librarian'
        )
        db.session.add(user)
        db.session.commit()
        return user
    
@pytest.fixture
def sample_book(app):
    """
    Create a sample book in the database.
    
    Returns:
        Book: A book object with title='Test Book'
    """
    with app.app_context():
        book = Book(
            title='Test Book',
            author='Test Author',
            isbn='1234567890',
            total_copies=3,
            available_copies=3
        )
        db.session.add(book)
        db.session.commit()
        db.session.refresh(book)
        db.session.expunge(book)        
        return book


@pytest.fixture
def multiple_books(app):
    """
    Create multiple books in the database.
    
    Returns:
        list: List of Book objects
    """
    with app.app_context():
        books = [
            Book(title='Book 1', author='Author A', isbn='1111111111', total_copies=2, available_copies=2),
            Book(title='Book 2', author='Author B', isbn='2222222222', total_copies=1, available_copies=1),
            Book(title='Book 3', author='Author C', isbn='3333333333', total_copies=5, available_copies=5),
        ]
        for book in books:
            db.session.add(book)
        db.session.commit()
        return books

@pytest.fixture
def sample_loan(app, sample_user, sample_book):
    """
    Create a sample loan in the database.
    
    Returns:
        Loan: A loan object linking sample_user and sample_book
    """
    with app.app_context():
        # Refresh objects in current session
        user = db.session.merge(sample_user)
        book = db.session.merge(sample_book)
        
        loan = Loan(
            user_id=user.id,
            book_id=book.id
        )
        
        # Update book availability
        book.available_copies -= 1
        
        db.session.add(loan)
        db.session.commit()
        db.session.refresh(loan)
        db.session.expunge(loan)
        return loan


@pytest.fixture
def overdue_loan(app, sample_user, sample_book):
    """
    Create an overdue loan (due date in the past).
    
    Returns:
        Loan: An overdue loan object
    """
    with app.app_context():
        user = db.session.merge(sample_user)
        book = db.session.merge(sample_book)
        
        # Create a loan that's 5 days overdue
        loan = Loan(
            user_id=user.id,
            book_id=book.id,
            loan_date=datetime.utcnow() - timedelta(days=19),  
            due_date=datetime.utcnow() - timedelta(days=5)     
        )
        
        book.available_copies -= 1
        
        db.session.add(loan)
        db.session.commit()
        return loan


@pytest.fixture
def returned_loan(app, sample_user, sample_book):
    """
    Create a returned loan.
    
    Returns:
        Loan: A returned loan object with fine
    """
    with app.app_context():
        user = db.session.merge(sample_user)
        book = db.session.merge(sample_book)
        
        # Create a loan returned 3 days late
        loan = Loan(
            user_id=user.id,
            book_id=book.id,
            loan_date=datetime.utcnow() - timedelta(days=17),
            due_date=datetime.utcnow() - timedelta(days=3),
            return_date=datetime.utcnow(),
            fine=1.50  # 3 days × $0.50
        )
        
        db.session.add(loan)
        db.session.commit()
        return loan    
    
    