@echo off
REM Script to run the separate guest chatbot

REM Change to the project root directory
cd /d "%~dp0\.."

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Run the chatbot application
python backend\run_chatbot.py