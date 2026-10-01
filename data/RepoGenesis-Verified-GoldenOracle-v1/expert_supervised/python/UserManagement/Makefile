.PHONY: help install run run-docker test test-verbose clean db-init db-reset

help:
	@echo "User Management Microservice - Available Commands"
	@echo "=================================================="
	@echo "make install          - Install dependencies"
	@echo "make run              - Run the service locally"
	@echo "make run-docker       - Run the service in Docker"
	@echo "make test             - Run all tests"
	@echo "make test-verbose     - Run tests with verbose output"
	@echo "make clean            - Clean up temporary files"
	@echo "make db-init          - Initialize database"
	@echo "make db-reset         - Reset database"
	@echo "make lint             - Run linting"
	@echo "make format           - Format code"

install:
	python3 -m venv venv
	. venv/bin/activate && pip install --upgrade pip
	. venv/bin/activate && pip install -r requirements.txt

run:
	bash start.sh

run-docker:
	docker build -t user-management:latest .
	docker run -p 8081:8081 \
		-e FLASK_ENV=development \
		-e DATABASE_URL=sqlite:///user_management.db \
		user-management:latest

test:
	. venv/bin/activate && cd tests && pytest

test-verbose:
	. venv/bin/activate && cd tests && pytest -v -s

test-coverage:
	. venv/bin/activate && cd tests && pytest --cov=.. --cov-report=html

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf htmlcov
	rm -rf dist build *.egg-info
	rm -rf venv

db-init:
	. venv/bin/activate && python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.create_all()
    print("Database initialized")
EOF

db-reset:
	. venv/bin/activate && python3 << EOF
from app import create_app, db
app = create_app()
with app.app_context():
    db.drop_all()
    db.create_all()
    print("Database reset")
EOF

lint:
	. venv/bin/activate && flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

format:
	. venv/bin/activate && black . && isort .

