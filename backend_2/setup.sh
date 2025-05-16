#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Setting up AI Task Analysis System development environment...${NC}\n"

# Check if Python 3.11 is installed
if command -v python3.11 &>/dev/null; then
    echo -e "${GREEN}Python 3.11 found${NC}"
else
    echo -e "${RED}Python 3.11 is required but not found${NC}"
    echo "Please install Python 3.11 and try again"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "\n${YELLOW}Creating virtual environment...${NC}"
    python3.11 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "\n${GREEN}Virtual environment already exists${NC}"
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "\n${YELLOW}Upgrading pip...${NC}"
python -m pip install --upgrade pip

# Install dependencies
echo -e "\n${YELLOW}Installing dependencies...${NC}"
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cp .env.example .env
    echo -e "${GREEN}.env file created${NC}"
    echo -e "${YELLOW}Please update .env with your configuration${NC}"
else
    echo -e "\n${GREEN}.env file already exists${NC}"
fi

# Initialize database
echo -e "\n${YELLOW}Initializing database...${NC}"
python create_db.py

# Run tests
echo -e "\n${YELLOW}Running tests...${NC}"
pytest

# Final instructions
echo -e "\n${GREEN}Setup complete!${NC}"
echo -e "\nTo start the development server:"
echo -e "${YELLOW}$ source venv/bin/activate${NC}"
echo -e "${YELLOW}$ uvicorn app.main:app --reload${NC}"
echo -e "\nAPI documentation will be available at:"
echo -e "${YELLOW}http://localhost:8000/docs${NC}"
echo -e "${YELLOW}http://localhost:8000/redoc${NC}"

# Docker instructions
echo -e "\nTo run with Docker:"
echo -e "${YELLOW}$ docker-compose up -d${NC}"

# Make the script executable
chmod +x setup.sh

echo -e "\n${GREEN}Ready to start development!${NC}"
