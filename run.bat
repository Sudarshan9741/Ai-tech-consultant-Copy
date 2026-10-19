@echo off
echo =====================================================================
echo           Starting AI Tech Consultant Services (Tasks 1, 2, 3)
echo =====================================================================
echo.

rem Safe demo default: do not crawl the live sitemap automatically.
set TASK1_SCHEDULED_SYNC_ENABLED=false

echo [1/3] Starting Task 1: Knowledge Brain (Port 8000)...
curl.exe -s http://127.0.0.1:8000/health > nul 2>&1
if errorlevel 1 start "Task 1 - Knowledge Brain" /D "%~dp0task1-knowledge-brain" cmd.exe /k python -m uvicorn app.main:app --host 127.0.0.1 --port 8000

ping 127.0.0.1 -n 4 > nul

echo [2/3] Starting Task 2: Inbox Agent (Port 3000)...
curl.exe -s http://127.0.0.1:3000/health > nul 2>&1
if errorlevel 1 start "Task 2 - Inbox Agent" /D "%~dp0task2-inbox-agent" cmd.exe /k npm start

ping 127.0.0.1 -n 3 > nul

echo [3/3] Starting Task 3: Meeting to Scope (Port 8001)...
curl.exe -s http://127.0.0.1:8001/health > nul 2>&1
if errorlevel 1 start "Task 3 - Meeting to Scope" /D "%~dp0task3-meeting-to-scope" cmd.exe /k python -m uvicorn app.main:app --host 127.0.0.1 --port 8001

ping 127.0.0.1 -n 3 > nul

echo.
echo =====================================================================
echo  All services are live:
echo  - Task 1 Knowledge Brain UI and API : http://127.0.0.1:8000
echo  - Task 2 Inbox Agent Dashboard      : http://127.0.0.1:3000
echo  - Task 3 Meeting to Scope UI and API: http://127.0.0.1:8001
echo =====================================================================
