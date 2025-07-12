#!/bin/bash

# Install dependencies
pip install \
--upgrade pip
pip install pyinstaller==6.14.*
python setup.py install
pip list

# Build and package the app using PyInstaller
pyinstaller \
--name CartPlayer \
--windowed \
--icon=app_icon_fullsize/app_icon_fullsize.icns \
--noconfirm \
--clean cart_player/__main__.py \
--add-data "cart_player/frontend/resources/files:cart_player/frontend/resources/files" \
--add-data "cart_player/backend/resources/files:cart_player/backend/resources/files"
