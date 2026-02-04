"""
Error handling utilities for LearnQuest API.
Provides decorators and helper functions for consistent error handling.
"""

from functools import wraps
from flask import request, jsonify, current_app
import logging

logger = logging.getLogger(__name__)


def error_response(message, status_code=400, error_code=None):
    """
    Create a standardized error response.
    
    Args:
        message (str): Human-readable error message
        status_code (int): HTTP status code
        error_code (str): Optional machine-readable error code
    
    Returns:
        tuple: (JSON response, status code)
    """
    response = {
        'success': False,
        'error': message,
        'status_code': status_code
    }
    if error_code:
        response['error_code'] = error_code
    return jsonify(response), status_code


def validate_json(required_fields=None, optional_fields=None):
    """
    Decorator to validate JSON request body.
    
    Args:
        required_fields (list): List of required field names
        optional_fields (list): List of optional field names
    
    Returns:
        decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Check if request has JSON content
            if not request.is_json:
                return error_response(
                    'Content-Type must be application/json',
                    415,
                    'INVALID_CONTENT_TYPE'
                )
            
            try:
                data = request.get_json()
            except Exception as e:
                logger.error(f"JSON parse error: {e}")
                return error_response(
                    'Invalid JSON in request body',
                    400,
                    'JSON_PARSE_ERROR'
                )
            
            if data is None:
                return error_response(
                    'Request body cannot be empty',
                    400,
                    'EMPTY_BODY'
                )
            
            # Validate required fields
            if required_fields:
                missing_fields = [field for field in required_fields 
                                 if field not in data or data[field] is None]
                if missing_fields:
                    return error_response(
                        f"Missing required fields: {', '.join(missing_fields)}",
                        400,
                        'MISSING_FIELDS'
                    )
            
            # Validate field types (basic validation)
            if required_fields or optional_fields:
                allowed_fields = set((required_fields or []) + (optional_fields or []))
                for field, value in data.items():
                    if field not in allowed_fields:
                        return error_response(
                            f"Unknown field: {field}",
                            400,
                            'UNKNOWN_FIELD'
                        )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def handle_db_errors(f):
    """
    Decorator to handle database errors consistently.
    
    Returns:
        decorator function
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from app import db
        try:
            return f(*args, **kwargs)
        except Exception as e:
            db.session.rollback()
            logger.error(f"Database error in {f.__name__}: {e}")
            
            # Handle specific database errors
            if 'UNIQUE constraint' in str(e) or 'duplicate' in str(e).lower():
                return error_response(
                    'A record with this value already exists',
                    409,
                    'DUPLICATE_ENTRY'
                )
            elif 'FOREIGN KEY constraint' in str(e):
                return error_response(
                    'Referenced resource does not exist',
                    400,
                    'INVALID_REFERENCE'
                )
            elif 'NOT NULL constraint' in str(e):
                return error_response(
                    'A required field is missing',
                    400,
                    'NULL_CONSTRAINT'
                )
            else:
                return error_response(
                    'A database error occurred. Please try again.',
                    500,
                    'DATABASE_ERROR'
                )
    return decorated_function


def validate_query_params(validation_rules):
    """
    Decorator to validate query parameters.
    
    Args:
        validation_rules (dict): Dict of param_name -> {type, min, max, allowed}
    
    Returns:
        decorator function
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = []
            
            for param, rules in validation_rules.items():
                value = request.args.get(param)
                
                # Check required
                if rules.get('required') and value is None:
                    errors.append(f"Query parameter '{param}' is required")
                    continue
                
                if value is None:
                    continue
                
                # Type conversion
                param_type = rules.get('type', str)
                try:
                    if param_type == int:
                        value = int(value)
                    elif param_type == float:
                        value = float(value)
                    elif param_type == bool:
                        value = value.lower() in ('true', '1', 'yes')
                except ValueError:
                    errors.append(f"Query parameter '{param}' must be of type {param_type.__name__}")
                    continue
                
                # Range validation
                if param_type in (int, float):
                    if 'min' in rules and value < rules['min']:
                        errors.append(f"Query parameter '{param}' must be >= {rules['min']}")
                    if 'max' in rules and value > rules['max']:
                        errors.append(f"Query parameter '{param}' must be <= {rules['max']}")
                
                # Allowed values validation
                if 'allowed' in rules and value not in rules['allowed']:
                    allowed = rules['allowed']
                    if isinstance(allowed, (list, tuple)):
                        allowed_str = ', '.join(str(a) for a in allowed)
                    else:
                        allowed_str = str(allowed)
                    errors.append(f"Query parameter '{param}' must be one of: {allowed_str}")
            
            if errors:
                return error_response(
                    '; '.join(errors),
                    400,
                    'INVALID_QUERY_PARAMS'
                )
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


class APIException(Exception):
    """
    Custom exception for API errors.
    
    Attributes:
        message: Error message
        status_code: HTTP status code
        error_code: Machine-readable error code
    """
    def __init__(self, message, status_code=400, error_code=None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


def admin_required(f):
    """
    Decorator to require admin role for an endpoint.
    Must be used AFTER @jwt_required() decorator.
    
    Usage:
        @app.route('/admin/users')
        @jwt_required()
        @admin_required
        def admin_users():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask_jwt_extended import get_jwt_identity
        from app.models.user import User
        
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        
        if not user:
            return error_response('User not found', 404, 'USER_NOT_FOUND')
        
        if user.role != 'admin':
            return error_response(
                'Admin access required',
                403,
                'ADMIN_REQUIRED'
            )
        
        return f(*args, **kwargs)
    return decorated_function
