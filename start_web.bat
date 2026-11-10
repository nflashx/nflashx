@echo off
setlocal
cd /d "%~dp0"

rem Optional local secrets file (gitignored):
rem   copy secrets.env.example secrets.env
rem   then fill in the real AGNES_KEY / ADMIN_KEY values.
if exist "secrets.env" call "secrets.env"

if not "%AGNES_KEY%"=="" goto :check_admin
echo [ERROR] AGNES_KEY is not set.
echo   set AGNES_KEY=sk-...
echo   or put it in secrets.env and run start_web.bat again.
goto :fail

:check_admin
if not "%ADMIN_KEY%"=="" goto :run
echo [ERROR] ADMIN_KEY is not set.
echo   set ADMIN_KEY=nfx-admin-...
echo   or put it in secrets.env and run start_web.bat again.
goto :fail

:run
if "%PORT%"=="" set PORT=8600
echo [*] Starting NFlashX on port %PORT% ...
python -I server.py
goto :eof

:fail
echo.
pause
exit /b 1
