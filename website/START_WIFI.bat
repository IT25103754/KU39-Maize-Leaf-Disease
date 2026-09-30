@echo off
setlocal
cd /d "%~dp0"
set MAIZE_HOST=0.0.0.0
set MAIZE_PORT=5000
echo Connect phones and laptops to the same Wi-Fi.
echo Find IPv4 Address under Wireless LAN adapter Wi-Fi below.
echo On the other device open http://YOUR-WIFI-IP:5000
ipconfig
call START_WEBSITE.bat
