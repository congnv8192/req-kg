"""
Error handling utilities for User Management Service
"""
from flask import jsonify


class CustomError(Exception):
    """Base custom error class"""
    def __init__(self, message, code='error', status_code=400, details=None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class ValidationError(CustomError):
    """Validation error"""
    def __init__(self, message, code='validation_error', details=None):
        super().__init__(message, code, 422, details)


class NotFoundError(CustomError):
    """Not found error"""
    def __init__(self, message='Resource not found'):
        super().__init__(message, 'not_found', 404)


class ConflictError(CustomError):
    """Conflict error (duplicate resource)"""
    def __init__(self, message='Resource conflict'):
        super().__init__(message, 'conflict', 409)


class AuthenticationError(CustomError):
    """Authentication error"""
    def __init__(self, message, code='authentication_failed', status_code=401):
        super().__init__(message, code, status_code)


def handle_error(message, code, status_code, details=None):
    """
    Handle error response
    """
    error_response = {
        'error': {
            'code': code,
            'message': message
        }
    }
    
    if details:
        error_response['error']['details'] = details
    
    return jsonify(error_response), status_code


def handle_validation_errors(errors):
    """
    Handle multiple validation errors
    """
    details = {}
    for field, error_list in errors.items():
        details[field] = error_list[0] if error_list else 'Invalid value'
    
    error_response = {
        'error': {
            'code': 'validation_error',
            'message': 'Validation failed',
            'details': details
        }
    }
    
    return jsonify(error_response), 422

