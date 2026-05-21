#!/bin/bash

echo "Starting EDI Backend Automated Setup..."

# 1. Create Virtual Environment
echo "Creating virtual environment..."
python3 -m venv venv

# 2. Activate Environment and Install Requirements
echo "Installing locked dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 3. Create .env file automatically from template
if [ ! -f .env ]; then
    echo "Creating configuration .env file from template..."
    cp .env.example .env
else
    echo ".env file already exists. Skipping."
fi

echo "Setup Complete! To start your environment, run:"
echo "source venv/bin/activate && python3 server/main.py"