@echo off
setlocal
set "ROOT=%~dp0"

start "AoE Hotkey Editor - Backend"  powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '=== Django Backend ===' -ForegroundColor Cyan; try { Set-Location '%ROOT%src'; & '%ROOT%.venv\Scripts\python.exe' manage.py runserver } finally { Write-Host ''; Read-Host 'Press Enter to close' }"

start "AoE Hotkey Editor - Frontend" powershell -NoProfile -ExecutionPolicy Bypass -Command "Write-Host '=== React Frontend ===' -ForegroundColor Green; try { Set-Location '%ROOT%src\frontend'; npm run start } finally { Write-Host ''; Read-Host 'Press Enter to close' }"

endlocal
