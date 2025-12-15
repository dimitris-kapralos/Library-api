"""
Pytest configuration and shared fixtures for testing.
"""

import pytest
from app import app as flask_app
from database import db, User

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
    
    