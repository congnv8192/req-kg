#!/bin/bash

# User Management Service Start Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}User Management Service${NC}"
echo -e "${GREEN}================================${NC}"

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${YELLOW}Python version:${NC}"
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Install/update requirements
echo -e "${YELLOW}Installing dependencies...${NC}"
pip install --upgrade pip setuptools wheel > /dev/null 2>&1
pip install -r requirements.txt

# Initialize database
echo -e "${YELLOW}Initializing database...${NC}"
python3 -c "from database import init_db; init_db()"

# Check if database file was created
if [ -f "test.db" ]; then
    echo -e "${GREEN}✓ Database initialized${NC}"
fi

# Install test requirements
echo -e "${YELLOW}Installing test dependencies...${NC}"
pip install -r tests/requirements.txt > /dev/null 2>&1

# Set environment variables if not already set
export API_BASE_URL=${API_BASE_URL:-"http://localhost:8080/api/v1"}
export API_HOST=${API_HOST:-"0.0.0.0"}
export API_PORT=${API_PORT:-8080}
export JWT_SECRET_KEY=${JWT_SECRET_KEY:-"your-secret-key-change-in-production"}

# Display configuration
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Configuration:${NC}"
echo -e "${GREEN}================================${NC}"
echo "API Host: $API_HOST"
echo "API Port: $API_PORT"
echo "API Base URL: $API_BASE_URL"
echo "Database: SQLite (test.db)"

# Start the application
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}Starting application...${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# Run the FastAPI application with uvicorn
python3 -m uvicorn main:app --host "$API_HOST" --port "$API_PORT" --reload &
SERVER_PID=$!

# Give the server time to start
sleep 3

# Check if server is running
if ps -p $SERVER_PID > /dev/null; then
    echo -e "${GREEN}✓ Application started successfully (PID: $SERVER_PID)${NC}"
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}API Documentation:${NC}"
    echo -e "${GREEN}================================${NC}"
    echo "Swagger UI: http://localhost:$API_PORT/docs"
    echo "ReDoc: http://localhost:$API_PORT/redoc"
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}Running tests...${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    
    # Wait a bit more for the server to fully initialize
    sleep 2
    
    # Run tests
    cd tests
    python3 -m pytest -v --tb=short
    TEST_EXIT_CODE=$?
    cd ..
    
    # Kill the server
    kill $SERVER_PID 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}================================${NC}"
    if [ $TEST_EXIT_CODE -eq 0 ]; then
        echo -e "${GREEN}✓ All tests passed!${NC}"
    else
        echo -e "${RED}✗ Some tests failed${NC}"
    fi
    echo -e "${GREEN}================================${NC}"
    
    exit $TEST_EXIT_CODE
else
    echo -e "${RED}✗ Failed to start application${NC}"
    exit 1
fi

