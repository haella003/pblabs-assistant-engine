@echo off
echo Starting EDI Backend Automated Setup...

:: 1. Create Virtual Environment
echo Creating virtual environment...
python -m venv venv

:: 2. Activate Environment and Install Requirements
echo Installing locked dependencies...
call venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

:: 3. Create .env file automatically from template
if not exist .env (
    echo Creating configuration .env file from template...
    copy .env.example .env
) else (
    echo .env file already exists. Skipping.
)

echo Setup Complete! To start your environment, run:
echo venv\Scripts\activate ^&^& python server/main.py