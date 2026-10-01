#!/bin/bash

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  RBAC Service Test Runner${NC}"
echo -e "${BLUE}==========================================${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Please run 'bash start.sh' first.${NC}"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if service is running
echo -e "${YELLOW}Checking if service is running on http://localhost:8080...${NC}"
if ! python3 -c "import requests; requests.get('http://localhost:8080/', timeout=2)" 2>/dev/null; then
    echo -e "${RED}ERROR: Service is not running on http://localhost:8080${NC}"
    echo -e "${YELLOW}Please start the service with: bash start.sh${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Service is running${NC}"
echo ""

# Run tests
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Running Test Suite${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

cd tests
python test_rbac_service.py

echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Test Run Complete${NC}"
echo -e "${BLUE}==========================================${NC}"

