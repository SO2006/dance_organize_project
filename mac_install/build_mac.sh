#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Checking dependencies..."
pip3 install pyinstaller streamlit pandas numpy plotly openpyxl altair --quiet

cp ../danceui.py .

echo "Building DanceUI for macOS..."
python3 -m PyInstaller danceui_mac.spec --clean --noconfirm

echo ""
echo "Build complete!"
echo ""
echo "The app is at: dist/DanceUI.app"
echo ""
echo "To run it:            open dist/DanceUI.app"
echo "To distribute:        zip -r DanceUI_mac.zip dist/DanceUI.app"
echo ""
echo "NOTE: On first run on another Mac, the user may need to right-click"
echo "the app and choose 'Open' to bypass Gatekeeper security warning."
