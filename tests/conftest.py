"""
Pytest configuration and fixtures for LearnQuest tests.
"""

import pytest
from app import create_app, db
from app.models.user import User
from flask_jwt_extended import create_access_token


@pytest.fixture
def app():
    """
    Create and configure a Flask app for testing.
    """
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-secret-key'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(app):
    """
    Create a test client for the Flask app.
    """
    return app.test_client()


@pytest.fixture
def test_user(app):
    """
    Create a test user in the database.
    Cleans up after the test.
    """
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            role='learner'
        )
        user.set_password('testpassword123')
        
        db.session.add(user)
        db.session.commit()
        
        user_id = user.id
        
        yield user
        
        # Cleanup: delete the test user
        User.query.filter_by(id=user_id).delete()
        db.session.commit()


@pytest.fixture
def auth_headers(test_user):
    """
    Create JWT authorization headers for the test user.
    """
    access_token = create_access_token(identity=test_user.id)
    return {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }


@pytest.fixture
def new_user_data():
    """
    Return valid registration data for a new user.
    """
    return {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password': 'securepassword123'
    }


@pytest.fixture
def existing_user_data():
    """
    Return registration data matching the test user.
    """
    return {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'somepassword'
    }

