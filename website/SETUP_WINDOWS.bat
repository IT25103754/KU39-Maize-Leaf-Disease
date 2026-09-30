@echo off
setlocal
cd /d "%~dp0"
echo MaizeLens - first-time setup. Internet is required.
py -3.12 --version >nul 2>&1
if errorlevel 1 (
 echo Install Python 3.12 64-bit with the Python launcher from python.org first.
 pause
 exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
 py -3.12 -m venv .venv
 if errorlevel 1 goto failed
)
.venv\Scripts\python.exe -m pip install --upgrade pip
if errorlevel 1 goto failed
.venv\Scripts\python.exe -m pip install -r requirements.txt
if errorlevel 1 goto failed
echo Setup complete. Now double-click START_WEBSITE.bat.
pause
exit /b 0
:failed
echo Setup failed. Share the error above.
pause
exit /b 1
