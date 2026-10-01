"""
API routes for User Management Service
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
from models import User, RoleEnum, StatusEnum
from extensions import db
from utils.validators import (
    validate_username, validate_email, validate_password,
    validate_full_name, validate_phone, validate_role, validate_status,
    validate_pagination
)
from utils.error_handler import (
    ValidationError, NotFoundError, ConflictError, AuthenticationError, handle_error
)
from utils.auth import generate_token, verify_token
from sqlalchemy import or_, and_

api_bp = Blueprint('api', __name__)


@api_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0',
        'database': 'connected'
    }), 200


@api_bp.route('/users', methods=['POST'])
def create_user():
    """Create new user"""
    data = request.get_json()
    
    if data is None:
        return handle_error('Invalid JSON', 'invalid_json', 400)
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'full_name', 'role']
    for field in required_fields:
        if field not in data or data[field] is None:
            raise ValidationError(f'{field} is required', details={field: f'{field} is required'})
    
    # Validate username
    is_valid, error = validate_username(data['username'])
    if not is_valid:
        current_app.logger.error(f"Username validation failed: {error}")
        raise ValidationError(error, details={'username': error})
    
    # Validate email
    is_valid, error = validate_email(data['email'])
    if not is_valid:
        current_app.logger.error(f"Email validation failed: {error}")
        raise ValidationError(error, details={'email': error})
    
    # Validate password
    is_valid, error = validate_password(data['password'])
    if not is_valid:
        current_app.logger.error(f"Password validation failed: {error}")
        raise ValidationError(error, details={'password': error})
    
    # Validate full name
    is_valid, error = validate_full_name(data['full_name'])
    if not is_valid:
        current_app.logger.error(f"Full name validation failed: {error}")
        raise ValidationError(error, details={'full_name': error})
    
    # Validate role
    is_valid, error = validate_role(data['role'])
    if not is_valid:
        current_app.logger.error(f"Role validation failed: {error}")
        raise ValidationError(error, details={'role': error})
    
    # Validate phone if provided
    if 'phone' in data and data['phone']:
        is_valid, error = validate_phone(data['phone'])
        if not is_valid:
            raise ValidationError(error, details={'phone': error})
    
    # Check for duplicate username
    if db.session.execute(db.select(User).filter_by(username=data['username'])).scalar_one_or_none():
        raise ConflictError('Username already exists')
    
    # Check for duplicate email
    if db.session.execute(db.select(User).filter_by(email=data['email'])).scalar_one_or_none():
        raise ConflictError('Email already exists')
    
    # Create user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name'],
        role=data['role'],
        phone=data.get('phone'),
        status='active'
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    return jsonify(user.to_dict()), 201


@api_bp.route('/users', methods=['GET'])
def get_users():
    """Get users list with pagination and filtering"""
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    status = request.args.get('status', None, type=str)
    role = request.args.get('role', None, type=str)
    search = request.args.get('search', None, type=str)
    
    # Validate pagination
    is_valid, error, page, limit = validate_pagination(page, limit)
    if not is_valid:
        raise ValidationError(error)
    
    # Build query
    query = User.query
    
    # Filter by status
    if status:
        is_valid, error = validate_status(status)
        if not is_valid:
            raise ValidationError(error, details={'status': error})
        query = query.filter_by(status=status)
    
    # Filter by role
    if role:
        is_valid, error = validate_role(role)
        if not is_valid:
            raise ValidationError(error, details={'role': error})
        query = query.filter_by(role=role)
    
    # Search
    if search:
        search_term = f'%{search}%'
        query = query.filter(or_(
            User.username.ilike(search_term),
            User.email.ilike(search_term),
            User.full_name.ilike(search_term)
        ))
    
    # Pagination
    total = query.count()
    users_page = query.offset((page - 1) * limit).limit(limit).all()
    
    pages = (total + limit - 1) // limit
    
    return jsonify({
        'users': [user.to_dict() for user in users_page],
        'pagination': {
            'page': page,
            'limit': limit,
            'total': total,
            'pages': pages
        }
    }), 200


@api_bp.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """Get single user by ID"""
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    
    return jsonify(user.to_dict()), 200


@api_bp.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """Update user information"""
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    
    data = request.get_json()
    if data is None:
        return handle_error('Invalid JSON', 'invalid_json', 400)
    
    # Validate and update username
    if 'username' in data:
        is_valid, error = validate_username(data['username'])
        if not is_valid:
            raise ValidationError(error, details={'username': error})
        
        # Check for duplicate username
        existing = User.query.filter_by(username=data['username']).first()
        if existing and existing.id != user_id:
            raise ConflictError('Username already exists')
        
        user.username = data['username']
    
    # Validate and update email
    if 'email' in data:
        is_valid, error = validate_email(data['email'])
        if not is_valid:
            raise ValidationError(error, details={'email': error})
        
        # Check for duplicate email
        existing = User.query.filter_by(email=data['email']).first()
        if existing and existing.id != user_id:
            raise ConflictError('Email already exists')
        
        user.email = data['email']
    
    # Validate and update full name
    if 'full_name' in data:
        is_valid, error = validate_full_name(data['full_name'])
        if not is_valid:
            raise ValidationError(error, details={'full_name': error})
        user.full_name = data['full_name']
    
    # Validate and update role
    if 'role' in data:
        is_valid, error = validate_role(data['role'])
        if not is_valid:
            raise ValidationError(error, details={'role': error})
        user.role = data['role']
    
    # Validate and update phone
    if 'phone' in data:
        if data['phone']:
            is_valid, error = validate_phone(data['phone'])
            if not is_valid:
                raise ValidationError(error, details={'phone': error})
        user.phone = data.get('phone')
    
    # Validate and update status
    if 'status' in data:
        is_valid, error = validate_status(data['status'])
        if not is_valid:
            raise ValidationError(error, details={'status': error})
        user.status = data['status']
    
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify(user.to_dict()), 200


@api_bp.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """Delete user"""
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    
    db.session.delete(user)
    db.session.commit()
    
    return jsonify({'message': 'User deleted successfully'}), 200


@api_bp.route('/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.get_json()
    
    if data is None:
        return handle_error('Invalid JSON', 'invalid_json', 400)
    
    # Validate required fields
    if 'username' not in data or not data['username']:
        raise ValidationError('Username is required', details={'username': 'Username is required'})
    
    if 'password' not in data or not data['password']:
        raise ValidationError('Password is required', details={'password': 'Password is required'})
    
    username = data['username'].strip()
    password = data['password']
    
    if not username or not password:
        raise ValidationError('Username and password cannot be empty', details={
            'username': 'Username cannot be empty',
            'password': 'Password cannot be empty'
        })
    
    # Find user by username (case-insensitive)
    user = User.query.filter(User.username.ilike(username)).first()
    
    if not user:
        raise AuthenticationError('Invalid credentials', 'authentication_failed', 401)
    
    # Verify password
    if not user.verify_password(password):
        raise AuthenticationError('Invalid credentials', 'authentication_failed', 401)
    
    # Check user status
    if user.status == 'inactive':
        raise AuthenticationError('Account is inactive', 'account_inactive', 403)
    
    if user.status == 'suspended':
        raise AuthenticationError('Account is suspended', 'account_suspended', 403)
    
    # Generate token
    token, expires_in = generate_token(user.id)
    
    return jsonify({
        'access_token': token,
        'token_type': 'Bearer',
        'expires_in': expires_in,
        'user': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role
        }
    }), 200


@api_bp.route('/users/<int:user_id>/reset-password', methods=['POST'])
def reset_password(user_id):
    """Reset user password"""
    user = User.query.get(user_id)
    if not user:
        raise NotFoundError('User not found')
    
    data = request.get_json()
    if data is None:
        return handle_error('Invalid JSON', 'invalid_json', 400)
    
    if 'new_password' not in data or not data['new_password']:
        raise ValidationError('new_password is required', details={'new_password': 'new_password is required'})
    
    # Validate new password
    is_valid, error = validate_password(data['new_password'])
    if not is_valid:
        raise ValidationError(error, details={'new_password': error})
    
    # Set new password
    user.set_password(data['new_password'])
    user.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({'message': 'Password reset successfully'}), 200


@api_bp.errorhandler(400)
def bad_request(error):
    """Handle bad request"""
    return handle_error('Bad request', 'bad_request', 400)


@api_bp.errorhandler(404)
def not_found(error):
    """Handle not found"""
    return handle_error('Endpoint not found', 'not_found', 404)

