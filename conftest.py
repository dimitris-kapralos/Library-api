"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
from app import app as flask_app
from database import db, User, Book

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

    