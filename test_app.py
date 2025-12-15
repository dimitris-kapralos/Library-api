"""
Integration tests for the Library Management System.
Tests all API endpoints and business logic.
"""

import json

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



    
