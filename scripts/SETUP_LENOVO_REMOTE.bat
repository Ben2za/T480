@echo off
setlocal
cd /d "%~dp0"
set "LOG=%~dp0SETUP_LENOVO_REMOTE.log"
set "BUILD=2026-08-04.4"

echo ============================================================ >> "%LOG%"
echo Started %DATE% %TIME% >> "%LOG%"
echo Bootstrap build: %BUILD% >> "%LOG%"
echo Script drive: %~d0 >> "%LOG%"

powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -File "%~dp0SETUP_LENOVO_REMOTE.ps1" >> "%LOG%" 2>&1
set "RESULT=%ERRORLEVEL%"

echo Finished %DATE% %TIME% with exit code %RESULT% >> "%LOG%"
echo.
type "%LOG%"
echo.
if not "%RESULT%"=="0" echo SETUP FAILED - keep the log file for diagnosis.
if "%RESULT%"=="0" echo SETUP COMPLETE - leave the Lenovo powered on and connected to Wi-Fi.
pause
exit /b %RESULT%
