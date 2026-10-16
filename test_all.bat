@echo off
echo =====================================================================
echo           Executing Full Test Suite (Tasks 1, 2, 3)
echo =====================================================================
echo.

echo --- Running Task 1: Knowledge Brain Tests ---
cd /d "%~dp0task1-knowledge-brain"
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo [ERROR] Task 1 Tests Failed!
    exit /b %errorlevel%
)

echo.
echo --- Running Task 2: Inbox Agent Tests ---
cd /d "%~dp0task2-inbox-agent"
call npm test
if %errorlevel% neq 0 (
    echo [ERROR] Task 2 Tests Failed!
    exit /b %errorlevel%
)

echo.
echo --- Running Task 3: Meeting to Scope Tests ---
cd /d "%~dp0task3-meeting-to-scope"
python -m pytest tests/ -v
if %errorlevel% neq 0 (
    echo [ERROR] Task 3 Tests Failed!
    exit /b %errorlevel%
)

echo.
echo =====================================================================
echo  ALL 3 TASKS PASSED AUTOMATED TESTS SUCCESSFULLY!
echo =====================================================================
cd /d "%~dp0"
