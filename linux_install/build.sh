#!/bin/bash
set -e

cd "$(dirname "$0")"

echo "Building DanceUI standalone executable..."
pyinstaller danceui.spec --clean --noconfirm

echo ""
echo "Build complete. Executable is in: dist/DanceUI/"
echo "To run it on any Linux machine:"
echo "  ./dist/DanceUI/DanceUI"
echo ""
echo "To distribute, zip the entire dist/DanceUI/ folder."
