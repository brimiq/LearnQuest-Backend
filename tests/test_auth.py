"""
Comprehensive pytest tests for the LearnQuest authentication system.

Tests cover:
- User registration (success, duplicates, validation)
- User login (success, wrong password, nonexistent user)
- Current user retrieval (authenticated, no token)
"""

import pytest
from app.models.user import User


class TestUserRegistration:
    """Tests for user registration endpoint."""

    def test_register_success(self, test_client, new_user_data):
        """
        Test that valid registration returns 201 and user data.
        
        Expected:
        - Status code: 201 Created
        - Response contains 'message', 'user', and 'access_token'
        - User is created in database
        """
        response = test_client.post(
            '/api/auth/register',
            json=new_user_data
        )
        
        assert response.status_code == 201
        
        data = response.get_json()
        assert 'message' in data
        assert 'user' in data
        assert 'access_token' in data
        assert data['user']['username'] == new_user_data['username']
        assert data['user']['email'] == new_user_data['email']
        assert 'password' not in data['user']
        assert 'password_hash' not in data['user']
        
        # Verify user was created in database
        with test_client.application.app_context():
            user = User.query.filter_by(email=new_user_data['email']).first()
            assert user is not None
            assert user.username == new_user_data['username']

    def test_register_duplicate_email(self, test_client, test_user, new_user_data):
        """
        Test that registering with an existing email returns 409 conflict.
        
        Setup:
        - A test user already exists with email 'test@example.com'
        
        Expected:
        - Status code: 409 Conflict
        - Response contains 'error' about email already registered
        """
        # Use the email from test_user
        new_user_data['email'] = 'test@example.com'
        
        response = test_client.post(
            '/api/auth/register',
            json=new_user_data
        )
        
        assert response.status_code == 409
        
        data = response.get_json()
        assert 'error' in data
        assert 'email' in data['error'].lower()

    def test_register_duplicate_username(self, test_client, test_user, new_user_data):
        """
        Test that registering with an existing username returns 409 conflict.
        
        Setup:
        - A test user already exists with username 'testuser'
        
        Expected:
        - Status code: 409 Conflict
        - Response contains 'error' about username already taken
        """
        # Use the username from test_user
        new_user_data['username'] = 'testuser'
        
        response = test_client.post(
            '/api/auth/register',
            json=new_user_data
        )
        
        assert response.status_code == 409
        
        data = response.get_json()
        assert 'error' in data
        assert 'username' in data['error'].lower()

    def test_register_missing_username(self, test_client):
        """
        Test that registration with missing username returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/register',
            json={
                'email': 'test@example.com',
                'password': 'password123'
            }
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_register_missing_email(self, test_client):
        """
        Test that registration with missing email returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/register',
            json={
                'username': 'testuser',
                'password': 'password123'
            }
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_register_missing_password(self, test_client):
        """
        Test that registration with missing password returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/register',
            json={
                'username': 'testuser',
                'email': 'test@example.com'
            }
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_register_empty_body(self, test_client):
        """
        Test that registration with empty body returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/register',
            json={}
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_register_no_json(self, test_client):
        """
        Test that registration without JSON content returns appropriate error.
        Flask returns 415 UNSUPPORTED MEDIA TYPE when Content-Type is not application/json.
        """
        response = test_client.post(
            '/api/auth/register',
            data='not json',
            content_type='text/plain'
        )
        
        # Flask returns 415 UNSUPPORTED MEDIA TYPE when Content-Type is not application/json
        assert response.status_code in [400, 415]
        
        # get_json() may return None for certain error responses
        data = response.get_json() or {}
        assert 'error' in data or 'msg' in data or response.status_code == 415


class TestUserLogin:
    """Tests for user login endpoint."""

    def test_login_success(self, test_client, test_user):
        """
        Test that valid login credentials return 200 and access token.
        
        Setup:
        - A test user exists with password 'testpassword123'
        
        Expected:
        - Status code: 200 OK
        - Response contains 'message', 'user', and 'access_token'
        """
        response = test_client.post(
            '/api/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'testpassword123'
            }
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        assert 'user' in data
        assert 'access_token' in data
        assert data['user']['email'] == 'test@example.com'
        assert 'password' not in data['user']
        assert 'password_hash' not in data['user']

    def test_login_wrong_password(self, test_client, test_user):
        """
        Test that login with wrong password returns 401 unauthorized.
        
        Expected:
        - Status code: 401 Unauthorized
        - Response contains 'error' about invalid credentials
        """
        response = test_client.post(
            '/api/auth/login',
            json={
                'email': 'test@example.com',
                'password': 'wrongpassword'
            }
        )
        
        assert response.status_code == 401
        
        data = response.get_json()
        assert 'error' in data
        assert 'invalid' in data['error'].lower() or 'password' in data['error'].lower()

    def test_login_nonexistent_user(self, test_client):
        """
        Test that login with nonexistent user returns 401 unauthorized.
        
        Expected:
        - Status code: 401 Unauthorized
        - Response contains 'error' about invalid credentials
        """
        response = test_client.post(
            '/api/auth/login',
            json={
                'email': 'nonexistent@example.com',
                'password': 'somepassword'
            }
        )
        
        assert response.status_code == 401
        
        data = response.get_json()
        assert 'error' in data
        assert 'invalid' in data['error'].lower() or 'password' in data['error'].lower()

    def test_login_missing_email(self, test_client):
        """
        Test that login with missing email returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/login',
            json={
                'password': 'password123'
            }
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_login_missing_password(self, test_client):
        """
        Test that login with missing password returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/login',
            json={
                'email': 'test@example.com'
            }
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data

    def test_login_empty_body(self, test_client):
        """
        Test that login with empty body returns 400 bad request.
        """
        response = test_client.post(
            '/api/auth/login',
            json={}
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data


class TestCurrentUser:
    """Tests for current user endpoint."""

    def test_get_current_user_authenticated(self, test_client, test_user, auth_headers):
        """
        Test that authenticated user can retrieve their own data.
        
        Expected:
        - Status code: 200 OK
        - Response contains 'user' with correct data
        """
        response = test_client.get(
            '/api/auth/me',
            headers=auth_headers
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'user' in data
        assert data['user']['username'] == 'testuser'
        assert data['user']['email'] == 'test@example.com'
        assert 'password' not in data['user']
        assert 'password_hash' not in data['user']

    def test_get_current_user_no_token(self, test_client):
        """
        Test that request without token returns 401 unauthorized.
        
        Expected:
        - Status code: 401 Unauthorized
        - Response contains error message (Flask-JWT-Extended returns 'msg')
        """
        response = test_client.get('/api/auth/me')
        
        assert response.status_code == 401
        
        data = response.get_json()
        # Flask-JWT-Extended returns 'msg' instead of 'error'
        assert 'error' in data or 'msg' in data

    def test_get_current_user_invalid_token(self, test_client):
        """
        Test that request with invalid token returns appropriate error.
        
        Expected:
        - Status code: 401 or 422 (Flask-JWT-Extended returns 422 for invalid tokens)
        """
        response = test_client.get(
            '/api/auth/me',
            headers={
                'Authorization': 'Bearer invalid-token',
                'Content-Type': 'application/json'
            }
        )
        
        # Flask-JWT-Extended returns 422 UNPROCESSABLE ENTITY for invalid tokens
        assert response.status_code in [401, 422]
        
        data = response.get_json()
        assert 'error' in data or 'msg' in data

    def test_get_current_user_expired_token(self, test_client, app, test_user):
        """
        Test that request with expired token returns 401 unauthorized.
        
        Setup:
        - Create an access token that expires immediately
        
        Expected:
        - Status code: 401 Unauthorized
        """
        from flask_jwt_extended import create_access_token
        from datetime import timedelta
        
        # Create an already-expired token
        with app.app_context():
            expired_token = create_access_token(
                identity=test_user.id,
                expires_delta=timedelta(seconds=-1)
            )
        
        response = test_client.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {expired_token}',
                'Content-Type': 'application/json'
            }
        )
        
        assert response.status_code == 401


class TestRegistrationLoginIntegration:
    """Integration tests for registration and login flow."""

    def test_register_then_login(self, test_client):
        """
        Test that a user can register and then log in with the same credentials.
        
        Steps:
        1. Register a new user
        2. Login with the same credentials
        3. Verify both operations succeed
        """
        # Register a new user
        register_data = {
            'username': 'integrationtest',
            'email': 'integration@example.com',
            'password': 'testpassword123'
        }
        
        register_response = test_client.post(
            '/api/auth/register',
            json=register_data
        )
        
        assert register_response.status_code == 201
        register_data_response = register_response.get_json()
        assert register_data_response['user']['username'] == 'integrationtest'
        
        # Login with the same credentials
        login_response = test_client.post(
            '/api/auth/login',
            json={
                'email': 'integration@example.com',
                'password': 'testpassword123'
            }
        )
        
        assert login_response.status_code == 200
        login_data_response = login_response.get_json()
        assert login_data_response['user']['email'] == 'integration@example.com'
        assert 'access_token' in login_data_response
        
        # Verify the access token can be used to get user data
        me_response = test_client.get(
            '/api/auth/me',
            headers={
                'Authorization': f'Bearer {login_data_response["access_token"]}',
                'Content-Type': 'application/json'
            }
        )
        
        assert me_response.status_code == 200
        me_data = me_response.get_json()
        assert me_data['user']['username'] == 'integrationtest'

    def test_register_password_is_hashed(self, test_client, new_user_data):
        """
        Test that the password is properly hashed in the database.
        
        Expected:
        - Registration succeeds
        - Password in database is not in plaintext
        - Login works with original password
        """
        # Register user
        response = test_client.post(
            '/api/auth/register',
            json=new_user_data
        )
        
        assert response.status_code == 201
        
        # Verify password is hashed in database
        with test_client.application.app_context():
            user = User.query.filter_by(email=new_user_data['email']).first()
            assert user is not None
            assert user.password_hash != new_user_data['password']
            assert len(user.password_hash) > 50  # bcrypt hash is long
            # Verify password check works
            assert user.check_password(new_user_data['password']) is True
            # Verify wrong password fails
            assert user.check_password('wrongpassword') is False

