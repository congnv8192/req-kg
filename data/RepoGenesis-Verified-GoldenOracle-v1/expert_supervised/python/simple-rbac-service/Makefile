.PHONY: help install start stop test clean lint format docker-build docker-run

# Default target
help:
	@echo "Simple RBAC Service - Available Commands"
	@echo ""
	@echo "  make install      - Install dependencies"
	@echo "  make start        - Start the service"
	@echo "  make stop         - Stop the service"
	@echo "  make test         - Run test suite"
	@echo "  make lint         - Run code linting"
	@echo "  make format       - Format code"
	@echo "  make clean        - Clean up temporary files"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-run   - Run Docker container"
	@echo ""

# Install dependencies
install:
	@echo "Installing dependencies..."
	@python3 -m venv venv
	@. venv/bin/activate && pip install --upgrade pip
	@. venv/bin/activate && pip install -r requirements.txt
	@echo "Dependencies installed successfully"

# Start the service
start:
	@bash start.sh

# Stop the service
stop:
	@echo "Stopping service..."
	@pkill -f "python3 app.py" || echo "Service not running"

# Run tests
test:
	@bash run_tests.sh

# Run linting
lint:
	@echo "Running linting..."
	@. venv/bin/activate && pylint app.py config.py utils.py 2>/dev/null || echo "pylint not installed, skipping"
	@. venv/bin/activate && flake8 app.py config.py utils.py 2>/dev/null || echo "flake8 not installed, skipping"

# Format code
format:
	@echo "Formatting code..."
	@. venv/bin/activate && black app.py config.py utils.py 2>/dev/null || echo "black not installed, skipping"

# Clean temporary files
clean:
	@echo "Cleaning up..."
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete
	@find . -type f -name "*.pyo" -delete
	@find . -type f -name ".coverage" -delete
	@echo "Cleanup complete"

# Docker build
docker-build:
	@echo "Building Docker image..."
	@docker build -t simple-rbac-service:latest .
	@echo "Docker image built successfully"

# Docker run
docker-run: docker-build
	@echo "Running Docker container..."
	@docker run -p 8080:8080 simple-rbac-service:latest

# Quick start (install + start)
quickstart: install start

# Development setup
dev-setup: install
	@echo "Setting up development environment..."
	@. venv/bin/activate && pip install pylint flake8 black 2>/dev/null || true
	@echo "Development setup complete"

.PHONY: quickstart dev-setup

