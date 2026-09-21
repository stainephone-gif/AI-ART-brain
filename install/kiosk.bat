@echo off
rem Экран: Microsoft Edge в режиме киоска на локальной странице службы.
rem Порт должен совпадать с display.port в config.yaml.
timeout /t 20 /nobreak >nul
start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --kiosk http://127.0.0.1:8765/ --edge-kiosk-type=fullscreen --no-first-run --disable-features=TranslateUI --autoplay-policy=no-user-gesture-required
