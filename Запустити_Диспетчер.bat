@echo off
chcp 65001 >nul
title Штабний Диспетчер ПБД // Auto-Ingest Agent
color 0B
cls
echo ==============================================================================
echo        ШТАБНИЙ ДИСПЕТЧЕР // АГЕНТ АВТО-ПРИЙОМУ ЗВІТІВ ПБД (24/7)
echo ==============================================================================
echo.
echo [*] Запуск локального сервісу моніторингу звітів...
echo.

cd /d "%~dp0"

where python >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    python -u "dispatcher_service.py"
    goto :check_error
)

where py >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    py -3 -u "dispatcher_service.py"
    goto :check_error
)

if exist "%LOCALAPPDATA%\Programs\Python\Python315\python.exe" (
    "%LOCALAPPDATA%\Programs\Python\Python315\python.exe" -u "dispatcher_service.py"
    goto :check_error
)

echo [!] ПОМИЛКА: Python не знайдено у системному PATH!
echo     Будь ласка, встановіть Python або додайте його до змінних середовища.
pause
exit /b 1

:check_error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [!] Роботу диспетчера завершено з кодом помилки: %ERRORLEVEL%
    pause
)
