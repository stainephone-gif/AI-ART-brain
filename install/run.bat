@echo off
rem Запуск службы инсталляции (вызывается планировщиком задач при входе в систему).
cd /d "%~dp0\.."
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
:loop
".venv\Scripts\python.exe" apophenia.py run
echo apophenia.py завершился с кодом %errorlevel%, перезапуск через 30 с >> logs\restart.log
timeout /t 30 /nobreak >nul
goto loop
