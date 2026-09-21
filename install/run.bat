@echo off
rem Metasoznanie service (started by Task Scheduler at logon). Restarts apophenia.py if it exits.
cd /d "%~dp0\.."
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist logs mkdir logs
:loop
".venv\Scripts\python.exe" apophenia.py run
echo %date% %time% apophenia.py exited with code %errorlevel%, restart in 30 s >> logs\restart.log
timeout /t 30 /nobreak >nul
goto loop
