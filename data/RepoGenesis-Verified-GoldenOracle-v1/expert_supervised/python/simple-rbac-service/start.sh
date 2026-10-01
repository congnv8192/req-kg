#!/bin/bash

set -e

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Simple RBAC Service - Startup Script${NC}"
echo -e "${BLUE}==========================================${NC}"

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: Python 3 is not installed${NC}"
    echo "Please install Python 3 to run this service"
    exit 1
fi

echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"

# Check if venv exists, if not create it
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
fi

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --quiet --upgrade pip setuptools wheel

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
if [ -f "requirements.txt" ]; then
    pip install --quiet -r requirements.txt
    echo -e "${GREEN}✓ Dependencies installed${NC}"
else
    echo -e "${RED}ERROR: requirements.txt not found${NC}"
    exit 1
fi

# Check if app.py exists
if [ ! -f "app.py" ]; then
    echo -e "${RED}ERROR: app.py not found${NC}"
    exit 1
fi

echo -e "${GREEN}✓ All checks passed${NC}"
echo ""
echo -e "${BLUE}==========================================${NC}"
echo -e "${BLUE}  Starting RBAC Service${NC}"
echo -e "${BLUE}==========================================${NC}"
echo -e "${GREEN}Service will run on: http://0.0.0.0:8080${NC}"
echo -e "${YELLOW}Press Ctrl+C to stop the service${NC}"
echo -e "${BLUE}==========================================${NC}"
echo ""

# Run the application
python3 app.py

