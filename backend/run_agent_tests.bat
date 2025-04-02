@echo off
REM Run agent tests with pytest for Windows

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate
)

REM Navigate to backend directory
cd /d "%~dp0"

REM Install requirements if not already installed
pip install -r requirements.txt

REM Run pytest with async support
python -m pytest test_agents.py -v

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    deactivate
)