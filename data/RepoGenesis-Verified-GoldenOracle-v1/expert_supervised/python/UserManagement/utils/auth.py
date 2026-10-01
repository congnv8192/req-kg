"""
Authentication utilities for User Management Service
"""
import jwt
import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, current_app
from utils.error_handler import AuthenticationError


def generate_token(user_id, expires_in=None):
    """
    Generate JWT token
    """
    if expires_in is None:
        expires_in = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', timedelta(hours=24))
    
    if isinstance(expires_in, timedelta):
        expires_at = datetime.utcnow() + expires_in
        expires_in_seconds = int(expires_in.total_seconds())
    else:
        expires_in_seconds = expires_in
        expires_at = datetime.utcnow() + timedelta(seconds=expires_in)
    
    payload = {
        'user_id': user_id,
        'exp': expires_at,
        'iat': datetime.utcnow()
    }
    
    token = jwt.encode(
        payload,
        current_app.config['JWT_SECRET_KEY'],
        algorithm='HS256'
    )
    
    return token, expires_in_seconds


def verify_token(token):
    """
    Verify JWT token and return user_id
    """
    try:
        payload = jwt.decode(
            token,
            current_app.config['JWT_SECRET_KEY'],
            algorithms=['HS256']
        )
        return payload.get('user_id')
    except jwt.ExpiredSignatureError:
        raise AuthenticationError('Token has expired', 'token_expired', 401)
    except jwt.InvalidTokenError:
        raise AuthenticationError('Invalid token', 'invalid_token', 401)


def token_required(f):
    """
    Decorator to require valid token
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None
        
        # Check for token in Authorization header
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                raise AuthenticationError('Invalid authorization header', 'invalid_header', 401)
        
        if not token:
            raise AuthenticationError('Token is missing', 'missing_token', 401)
        
        user_id = verify_token(token)
        return f(user_id, *args, **kwargs)
    
    return decorated_function

