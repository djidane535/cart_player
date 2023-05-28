# Install dependencies
pip install --upgrade pip
pip install pyinstaller==5.7
python setup.py install
pip list

# Build and package the app using PyInstaller
pyinstaller --name CartPlayer --windowed --icon=app_icon_fullsize/app_icon_fullsize.ico cart_player/__main__.py

