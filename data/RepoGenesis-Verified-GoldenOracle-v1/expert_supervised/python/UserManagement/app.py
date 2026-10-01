"""
User Management Microservice
Main Flask application entry point
"""
import os
from flask import Flask
from flask_migrate import Migrate
from extensions import db, migrate
from datetime import timedelta
import logging
from logging.handlers import RotatingFileHandler


def create_app(config_name='development'):
    """Create and configure Flask application"""
    app = Flask(__name__)
    
    # Configuration
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'sqlite:///user_management.db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JSON_SORT_KEYS'] = False
    
    # JWT Configuration
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=int(os.getenv('JWT_EXPIRES_HOURS', 24)))
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    
    # Setup logging
    setup_logging(app)
    
    # Register blueprints
    from api import api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')
    
    # Register error handlers
    from utils.error_handler import CustomError, ValidationError, NotFoundError, ConflictError, AuthenticationError
    
    @app.errorhandler(CustomError)
    def handle_custom_error(error):
        response = jsonify({
            'error': {
                'code': error.code,
                'message': error.message
            }
        })
        if error.details:
            response.json['error']['details'] = error.details
        response.status_code = error.status_code
        return response
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Error handlers
    register_error_handlers(app)
    
    return app


def setup_logging(app):
    """Setup application logging"""
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler('logs/user_management.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('User Management Service started')


def register_error_handlers(app):
    """Register error handlers"""
    from utils.error_handler import handle_error, ValidationError, NotFoundError, ConflictError, AuthenticationError
    
    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return handle_error(error.message, error.code, 422, error.details)
    
    @app.errorhandler(NotFoundError)
    def handle_not_found_error(error):
        return handle_error(error.message, 'not_found', 404)
    
    @app.errorhandler(ConflictError)
    def handle_conflict_error(error):
        return handle_error(error.message, 'conflict', 409)
    
    @app.errorhandler(AuthenticationError)
    def handle_authentication_error(error):
        return handle_error(error.message, error.code, error.status_code)


if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=8081, debug=os.getenv('FLASK_ENV') == 'development')

