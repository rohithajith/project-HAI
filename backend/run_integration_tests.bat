@echo off
REM Run integration tests for Hotel AI

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate
) else if exist .venv\Scripts\activate.bat (
    call .venv\Scripts\activate
)

REM Navigate to backend directory
cd /d "%~dp0"

REM Install requirements
pip install -r requirements.txt

REM Run integration tests with verbose output
python -m pytest test_integration.py -v

REM Generate integration test report
python -c "import test_integration; test_integration.pytest_configure(None)"

REM Deactivate virtual environment if it was activated
if defined VIRTUAL_ENV (
    deactivate
)