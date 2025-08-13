#!/bin/bash

if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: You are not in a virtual environment."
    echo "Please activate your virtual environment before running this script."
    echo ""
    echo "To activate, run: source CONTRIBUTING.md#"
    exit 1
fi

echo 'Building the game with PyInstaller...'
pyinstaller --collect-all pgzero --windowed --onefile --clean src/main.py --name wibblo --add-data "src/images:images" --add-data "src/sounds:sounds" --add-data "src/fonts:fonts"
# pyinstaller --clean wibblo.spec