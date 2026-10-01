.PHONY: help install dev test test-fast test-coverage lint format clean docker-build docker-run

help:
	@echo "User Management Service - Available Commands"
	@echo "=============================================="
	@echo "make install        - Install dependencies"
	@echo "make dev            - Run in development mode"
	@echo "make test           - Run all tests"
	@echo "make test-fast      - Run tests without slow tests"
	@echo "make test-coverage  - Run tests with coverage report"
	@echo "make lint           - Run code linting"
	@echo "make format         - Format code with black"
	@echo "make clean          - Clean up temporary files"
	@echo "make docker-build   - Build Docker image"
	@echo "make docker-run     - Run Docker container"

install:
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	pip install -r tests/requirements.txt

dev:
	@echo "Starting development server..."
	python3 -m uvicorn main:app --host 0.0.0.0 --port 8080 --reload

test:
	@echo "Running all tests..."
	cd tests && pytest -v
	@echo "Test coverage report available in htmlcov/index.html"

test-fast:
	@echo "Running fast tests (skipping slow tests)..."
	cd tests && pytest -v -m "not slow"

test-coverage:
	@echo "Running tests with coverage..."
	cd tests && pytest -v --cov=../src --cov-report=html --cov-report=term-missing

lint:
	@echo "Running linting..."
	pylint **/*.py --disable=C0111,C0103,C0114,C0115,C0116 --fail-under=8.0

format:
	@echo "Formatting code..."
	black .
	isort .

clean:
	@echo "Cleaning up..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name htmlcov -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name ".coverage" -delete
	rm -rf dist/ build/ *.egg-info/

docker-build:
	@echo "Building Docker image..."
	docker build -t user-management:latest .

docker-run:
	@echo "Running Docker container..."
	docker run -p 8080:8080 \
		-e API_HOST=0.0.0.0 \
		-e API_PORT=8080 \
		-e JWT_SECRET_KEY=your-secret-key \
		user-management:latest

init-db:
	@echo "Initializing database..."
	python3 -c "from database import init_db; init_db()"
	@echo "Database initialized successfully"

db-clean:
	@echo "Removing database file..."
	rm -f test.db
	@echo "Database removed"

venv:
	@echo "Creating virtual environment..."
	python3 -m venv venv
	@echo "Virtual environment created. Activate with: source venv/bin/activate"

requirements-lock:
	@echo "Generating locked requirements..."
	pip freeze > requirements.lock

.DEFAULT_GOAL := help

