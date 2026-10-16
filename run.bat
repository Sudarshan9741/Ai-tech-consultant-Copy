@echo off
echo =====================================================================
echo           Starting AI Tech Consultant Services (Tasks 1, 2, 3)
echo =====================================================================
echo.

echo [1/3] Starting Task 1: Knowledge Brain (Port 8000)...
start "Task 1 - Knowledge Brain" cmd /k "cd /d "%~dp0task1-knowledge-brain" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000"

timeout /t 3 /nobreak > nul

echo [2/3] Starting Task 2: Inbox Agent (Port 3000)...
start "Task 2 - Inbox Agent" cmd /k "cd /d "%~dp0task2-inbox-agent" && npm start"

timeout /t 2 /nobreak > nul

echo [3/3] Starting Task 3: Meeting to Scope (Port 8001)...
start "Task 3 - Meeting to Scope" cmd /k "cd /d "%~dp0task3-meeting-to-scope" && python -m uvicorn app.main:app --host 127.0.0.1 --port 8001"

echo.
echo =====================================================================
echo  All services are live:
echo  - Task 1 Knowledge Brain UI & API : http://127.0.0.1:8000
echo  - Task 2 Inbox Agent Dashboard    : http://127.0.0.1:3000
echo  - Task 3 Meeting to Scope UI & API: http://127.0.0.1:8001
echo =====================================================================
