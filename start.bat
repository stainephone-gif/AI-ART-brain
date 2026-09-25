@echo off
rem Metasoznanie: start the service (minimized window) and the kiosk screen. Double-click to run.
cd /d "%~dp0"
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
if not exist ".venv\Scripts\python.exe" (
  echo .venv not found. Run first:  powershell -ExecutionPolicy Bypass -File install\install.ps1
  pause
  exit /b 1
)
start "Metasoznanie service" /min ".venv\Scripts\python.exe" apophenia.py run
timeout /t 15 /nobreak >nul
set EDGE="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist %EDGE% set EDGE="C:\Program Files\Microsoft\Edge\Application\msedge.exe"
if not exist %EDGE% (
  echo Microsoft Edge not found. Open http://127.0.0.1:8765/ in any browser and press F11.
  exit /b 0
)
start "" %EDGE% --kiosk http://127.0.0.1:8765/ --edge-kiosk-type=fullscreen --no-first-run --disable-features=TranslateUI
