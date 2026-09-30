@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
 echo Run SETUP_WINDOWS.bat first.
 pause
 exit /b 1
)
.venv\Scripts\python.exe -c "import json,urllib.request; r=json.load(urllib.request.urlopen('http://127.0.0.1:5000/api/health',timeout=5)); assert r.get('status')=='ready' and r.get('model')=='efficientnet_b0'" >nul 2>&1
if errorlevel 1 (
 echo First run START_WIFI.bat and wait for READY. Then run this file again.
 pause
 exit /b 1
)
where cloudflared >nul 2>&1
if errorlevel 1 (
 echo Install the official tunnel client once in Command Prompt:
 echo winget install --id Cloudflare.cloudflared --exact
 echo Then close this window and run this file again.
 echo Instructions are in SHARING_GUIDE.md.
 pause
 exit /b 1
)
echo Share the HTTPS trycloudflare.com link printed below.
echo This is a public demo link. Keep this and the website window open.
echo The link changes when restarted. Ctrl+C stops online sharing.
cloudflared tunnel --url http://127.0.0.1:5000
pause
