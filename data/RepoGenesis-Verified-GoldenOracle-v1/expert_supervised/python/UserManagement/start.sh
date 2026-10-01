#!/bin/bash

# User Management Microservice Startup Script
# This script will install dependencies, initialize the database, and start the service

set -e

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

print_status "User Management Microservice Starting..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    exit 1
fi

print_status "Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip --quiet

# Install dependencies
print_status "Installing dependencies from requirements.txt..."
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt --quiet
else
    print_error "requirements.txt not found"
    exit 1
fi

# Create logs directory
if [ ! -d "logs" ]; then
    print_status "Creating logs directory..."
    mkdir -p logs
fi

# Initialize database
print_status "Initializing database..."
python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized successfully")
EOF

# Clean up any existing test data
print_status "Setting up clean database..."
python3 << EOF
from app import create_app, db
from models import User
app = create_app()
with app.app_context():
    # Optional: Reset database on startup
    # db.drop_all()
    # db.create_all()
    user_count = User.query.count()
    print(f"Database ready with {user_count} existing users")
EOF

print_status "Starting User Management Microservice..."
print_status "Service will listen on http://localhost:8081"
print_status "API Base Path: /api/v1"
print_status "Health Check: http://localhost:8081/api/v1/health"
print_status ""
print_status "To run tests, in another terminal run:"
print_status "  cd tests && pytest -v"
print_status ""

# Start the Flask application
export FLASK_APP=app.py
export FLASK_ENV=development

python3 -m flask run --host=0.0.0.0 --port=8081

