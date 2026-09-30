@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run SETUP_WINDOWS.bat first.
 pause
 exit /b 1
)
.venv\Scripts\python.exe app.py
if errorlevel 1 (
 echo App could not start. Share the error above. See README for troubleshooting.
 pause
)
