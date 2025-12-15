"""
Integration tests for the Library Management System.
Tests all API endpoints and business logic.
"""

import json
from database import User

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
    
