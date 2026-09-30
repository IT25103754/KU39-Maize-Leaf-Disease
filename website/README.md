---
title: KU39 MaizeLens
emoji: 🌽
colorFrom: green
colorTo: yellow
sdk: docker
app_port: 7860
---

# Sharing update
See SHARING_GUIDE.md for Wi-Fi, temporary online links, and hosted deployment.
START_WEBSITE.bat still uses localhost by default. START_WIFI.bat enables LAN access.
The Docker deployment listens on port 7860. The original trained model is unchanged.

# MaizeLens - KU39 standalone maize leaf AI website

Your actual locked EfficientNetB0 model is included. No dataset, Colab, API key or retraining is required.

## Windows instructions
1. Extract the whole ZIP using Extract All. Do not run inside the ZIP.
2. Install **Python 3.12 (64-bit)** including the Python launcher if missing: https://www.python.org/downloads/windows/ .
3. Double-click **SETUP_WINDOWS.bat** once. Internet is required to install dependencies. TensorFlow is a large download.
4. Double-click **START_WEBSITE.bat**. Wait for the saved model to load.
5. The browser opens automatically at **http://127.0.0.1:5000**. If not, enter that address manually.
6. Choose/drop a JPG or PNG and click **Analyze leaf**.
7. Keep the command window open. Ctrl+C stops the website. On later visits run START_WEBSITE.bat only.

This runs as a local website on your laptop, not a public internet URL. CPU inference is used; no GPU is required. After setup the app itself does not need internet.

## Features
- Drag-and-drop or click-to-upload, image preview, replace/remove photo.
- Real saved-model prediction, four class scores, download result as JSON.
- Separate held-out accuracy and macro F1, clear model limitations.
- Invalid/empty/oversized file handling and model SHA-256 integrity check.
- Responsive desktop and mobile layout. No CDN fonts/assets.
- Uploaded photos are not retained by the app; upload processing may use temporary server buffers.

## Model contract
EXIF transpose, RGB conversion, PIL bilinear 224x224 resize, float32 RGB values 0-255. EfficientNet's scaling is internal. Never divide input values by 255 again. JPEG/PNG only, single-frame, <=8 MiB and <=25 million pixels.

Classes in output order: Blight, Common_Rust, Gray_Leaf_Spot, Healthy.
Held-out accuracy: 93.54%; macro F1: 0.9132; test images: 836.
A single-image score is not accuracy or a calibrated guarantee. Non-maize rejection and field validation are not implemented. Educational use; no treatment recommendations.

## Files
app.py: Flask API + actual Keras model + Waitress server.
templates/ and static/: browser interface.
model/: unchanged trained model and metadata.
requirements.txt: pinned runtime dependencies.
VALIDATION.json: tests performed and platform limitations.

## Troubleshooting
- Python missing: check `py -3.12 --version`. Install Python 3.12 x64 with its launcher.
- Missing modules: rerun SETUP_WINDOWS.bat and wait for success.
- Missing DLL/VCRUNTIME: install Microsoft Visual C++ 2015-2022 Redistributable x64, then retry. TensorFlow Windows instructions: https://www.tensorflow.org/install/pip .
- Port 5000 busy: close an earlier app window, or set MAIZE_PORT=5001 in the terminal before running.
- Model integrity error: extract a clean ZIP. Do not remove the check.
- The Windows batch files must be tried on your Windows machine; the application tests run in Linux x86-64 with Python 3.12.

## Terminal setup
python -m venv .venv
Windows activate: .venv\Scripts\activate
Linux activate: source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py

The dependency set is for x86-64 CPU use. Public hosting would require a separate server deployment; the included app binds only to localhost.
