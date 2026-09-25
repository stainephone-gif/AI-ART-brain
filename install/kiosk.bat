@echo off
rem Screen: Microsoft Edge in kiosk mode on the local service page. Port must match display.port in config.yaml.
timeout /t 20 /nobreak >nul
set EDGE="C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
if not exist %EDGE% set EDGE="C:\Program Files\Microsoft\Edge\Application\msedge.exe"
start "" %EDGE% --kiosk http://127.0.0.1:8765/ --edge-kiosk-type=fullscreen --no-first-run --disable-features=TranslateUI --autoplay-policy=no-user-gesture-required
