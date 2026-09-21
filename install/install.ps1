# Установка на Windows 10. Запускать из PowerShell в корне репозитория:
#   powershell -ExecutionPolicy Bypass -File install\install.ps1
# Нужны: Python 3.11+ (с галочкой "Add to PATH"), git (необязательно).
$ErrorActionPreference = "Stop"
Set-Location (Split-Path -Parent $PSScriptRoot)

if (-not (Test-Path ".venv")) { python -m venv .venv }
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

if (-not (Test-Path ".env")) { Copy-Item .env.example .env; Write-Host "Создан .env — впишите GIGACHAT_CREDENTIALS" }

# Сертификат НУЦ Минцифры для TLS к GigaChat (если ещё не скачан)
$cer = "install\russian_trusted_root_ca.cer"
if (-not (Test-Path $cer)) {
  try {
    Invoke-WebRequest -Uri "https://gu-st.ru/content/lending/russian_trusted_root_ca_pem.crt" -OutFile $cer
    Write-Host "Сертификат сохранён: $cer"
  } catch { Write-Host "Не удалось скачать сертификат автоматически; скачайте вручную (см. README) в $cer" }
}

if (-not (Test-Path "install\SumatraPDF.exe")) {
  Write-Host "Положите портативный SumatraPDF.exe в папку install\ (см. README) — он печатает PDF на HP LaserJet 1018"
}

Write-Host "`nПроверка без API и принтера:  .\.venv\Scripts\python.exe apophenia.py once --mock"
Write-Host "Пробный лист на принтер:      .\.venv\Scripts\python.exe apophenia.py test-print"
Write-Host "Автозапуск:                   powershell -ExecutionPolicy Bypass -File install\register_task.ps1"
