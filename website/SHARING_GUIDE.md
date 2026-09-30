# MaizeLens — Wi-Fi + online

## Update the existing Windows installation
Stop the old website window with Ctrl+C. Extract this ZIP, then copy its
KU39_Maize_Web contents INTO your existing KU39_Maize_Web folder and replace
matching files. Keep your existing Python environment; do not delete the old
folder. Dependencies have not changed, so setup does not need to run again.
If installing into a new folder, run SETUP_WINDOWS.bat once.

## 1. Same Wi-Fi
1. Double-click START_WIFI.bat (do not run START_WEBSITE at the same time).
2. Wait for READY. In the printed ipconfig output find Wireless LAN adapter
   Wi-Fi > IPv4 Address. Example only: 192.168.1.8.
3. Connect the phone/laptop to the same Wi-Fi. Open http://192.168.1.8:5000,
   replacing that example with YOUR IPv4 address. Do not use 127.0.0.1 on the phone.
4. If Windows asks, allow Python on your trusted Private network. Do not turn
   off the firewall. If blocked, check Windows Security > Firewall & network
   protection > Allow an app through firewall, and allow this Python on Private.
5. Guest networks/client isolation can block devices; use the same trusted
   non-guest network. No router port forwarding is required.
Keep the laptop awake and the website window open. IP can change after reconnecting.

## 2. Online demo link — works from different Wi-Fi/mobile data
This uses your laptop as the server. It is NOT permanent cloud hosting.
1. Leave START_WIFI.bat running and wait for READY.
2. Install Cloudflare's official tunnel client once in a new Command Prompt:

   winget install --id Cloudflare.cloudflared --exact

   If winget is unavailable, use the official Cloudflare downloads page below,
   install cloudflared, and ensure its directory is on PATH.
3. Close the installer terminal. Double-click START_ONLINE_LINK.bat.
4. Copy the https://...trycloudflare.com URL printed in that window.
5. Open it on a phone with Wi-Fi OFF/mobile data ON; upload a leaf and Analyze.
6. Share that URL with members. Keep BOTH windows open and the laptop online/awake.

The URL changes on restart. Anyone who has it can use the demo. This app has
no login. Cloudflare carries online traffic; it is not a local-only connection.
No account is required for Quick Tunnels. They are for testing/demo, without an
uptime guarantee. A pre-existing cloudflared config may prevent a Quick Tunnel;
consult official guidance before changing any existing tunnel configuration.

## 3. Stable hosted link — laptop can be off
The Dockerfile and README metadata are ready for a Hugging Face Docker Space.
A hosting account and an actual deployment are still required; this ZIP does
not itself create a public hosted URL. Use your own account; do not share passwords.

1. Sign in at https://huggingface.co and create a new Space.
2. Choose a name such as ku39-maizelens, SDK Docker / blank, and CPU hardware.
   Check the current hardware price before selecting anything paid.
3. Upload these items to the ROOT of the Space repository (not inside a
   KU39_Maize_Web parent folder):
   README.md, Dockerfile, requirements.txt, app.py,
   model/ (both files), templates/, static/.
   Do not upload the Python environment, dataset, or Windows launch scripts.
   Use the Space Files upload interface, preserving the folder names.
4. Commit the files and wait for Building -> Running. Check build/runtime logs
   if it reports an error. Model download is unnecessary: model.keras is included.
5. Use the Space's displayed app link; test on another device, then share it.
   For a Public Space, source code and model files are public as well as the app.
   Free hosted hardware may sleep when idle; this is not guaranteed always-on service.

## Verification
Wi-Fi: another device on the same network loads and predicts.
Online demo: a phone on mobile data loads and predicts.
Hosted: your laptop website is stopped, and the Space still loads and predicts.
Training, class order, preprocessing, and model weights are unchanged.
The 93.54% figure is recorded held-out test accuracy, not a guarantee per photo.

## Official references
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/do-more-with-tunnels/trycloudflare/
- https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/
- https://huggingface.co/docs/hub/spaces-sdks-docker
- https://huggingface.co/docs/hub/spaces-overview

## Validation limits
Backend inference tests are run locally. Windows BAT execution, a real second
Wi-Fi device, public tunnel connectivity, and the hosted Docker build must be
checked on the target systems. No hosted deployment has been created yet.
