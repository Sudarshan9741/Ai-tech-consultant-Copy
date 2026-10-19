@echo off
setlocal enabledelayedexpansion
echo =====================================================================
echo           Executing Full Test Suite (Tasks 1, 2, 3)
echo =====================================================================
echo.

set "TEST_ROOT=%TEMP%\ai-tech-consultant-tests-%RANDOM%"
mkdir "%TEST_ROOT%"
set "TASK1_DB_PATH=%TEST_ROOT%\knowledge_brain.db"
set "TASK1_CHECKPOINT_PATH=%TEST_ROOT%\crawl_checkpoint.json"
set "TASK1_SCHEDULED_SYNC_ENABLED=false"
set /a TASK1_TEST_PORT=8100 + (%RANDOM% %% 100)
set "TASK1_API_URL=http://127.0.0.1:%TASK1_TEST_PORT%"

echo --- [1/3] Running Task 1: Knowledge Brain Tests ---
cd /d "%~dp0task1-knowledge-brain"
python -m pytest tests/ -v
if !errorlevel! neq 0 (
    echo [ERROR] Task 1 Tests Failed!
    exit /b !errorlevel!
)

echo.
echo --- Starting isolated Task 1 API Server on Port %TASK1_TEST_PORT% ---
set STARTED_T1=0
curl.exe -s %TASK1_API_URL%/health > nul 2>&1
if !errorlevel! neq 0 (
    echo Starting Task 1 API server in background for integration tests...
    start "" /B python -m uvicorn app.main:app --host 127.0.0.1 --port %TASK1_TEST_PORT%
    set STARTED_T1=1
    rem Wait for server to respond
    for /l %%i in (1,1,15) do (
        curl.exe -s %TASK1_API_URL%/health > nul 2>&1
        if !errorlevel! equ 0 goto t1_ready
        timeout /t 1 /nobreak > nul
    )
)
:t1_ready
echo Task 1 API Server is live at %TASK1_API_URL%

echo.
echo --- [2/3] Running Task 2: Inbox Agent Tests ---
cd /d "%~dp0task2-inbox-agent"
call npm test
set T2_ERR=!errorlevel!

echo.
echo --- [3/3] Running Task 3: Meeting to Scope Tests ---
cd /d "%~dp0task3-meeting-to-scope"
python -m pytest tests/ -v
set T3_ERR=!errorlevel!

if !STARTED_T1! equ 1 (
    echo.
    echo Cleaning up background Task 1 server...
    for /f "tokens=5" %%a in ('netstat -aon ^| findstr :%TASK1_TEST_PORT% ^| findstr LISTENING') do taskkill /f /pid %%a > nul 2>&1
)

cd /d "%~dp0"
if exist "%TEST_ROOT%" rmdir /s /q "%TEST_ROOT%"

if !T2_ERR! neq 0 (
    echo [ERROR] Task 2 Tests Failed!
    exit /b !T2_ERR!
)

if !T3_ERR! neq 0 (
    echo [ERROR] Task 3 Tests Failed!
    exit /b !T3_ERR!
)

echo.
echo =====================================================================
echo  ALL 3 TASKS PASSED AUTOMATED TESTS SUCCESSFULLY!
echo =====================================================================
