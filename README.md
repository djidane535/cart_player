
# README

CartPlayer is an app for managing and playing your GameBoy, GameBoy Color and GameBoy Advance games using a physical cartridge reader.

The app has been designed to work with GBxCart RW, but will likely work with any cartridge reader compatible with FlashGBX (tested with ver. 3.22).

----

*This app should work correctly on Mac M1/M2 and Windows 11.*

*There is no release planned for any other platform.*

----

## User

See the [`Release`](https://github.com/djidane535/cart_player/releases) section to download the right version.

### Windows

- Download windows version of [FlashGBX](https://github.com/lesserkuma/FlashGBX/releases) (portable zip).
- Extract its content into `CartPlayer/` directory (*note: `CartPlayer.exe` and `FlashGBX.exe` should be within the same directory). 
- You can now launch the app by running `CartPlayer.exe`.

### Mac OSX

You need to install Python 3 and the python library `FlashGBX`.

When it's done, run `CartPlayer.app` (*note: you can copy it into your Applications like any other 3rd party app*).

#### Install Python 3

Follow instructions from the official website: [https://www.python.org/downloads/](https://www.python.org/downloads/)

#### Install FlashGBX

Open a terminal (`Terminal` on OSX, `Windows Powershell` on Windows) and type this:

```bash
# App has only been tested with this version 3.27
pip3 install FlashGBX==3.27  

# -- if it fails, try this one instead
pip install FlashGBX==3.27
```

## Developer

### Requirements

```bash
sudo port install py39-tkinter
sudo port install tk +quartz
```

### Setup

#### Setup virtual environment

```bash
conda create --name cart_player
conda activate cart_player
conda config --env --set subdir osx-64
conda install python=3.9
```

##### Install

```bash
pip install --upgrade pip
pip install -e ".[dev,tests]"
pre-commit install
```

##### Run pre-commit manually

```bash
pre-commit run --all-files
```

### Run

```bash
python -m cart_player
```

### Build

#### OSX

```bash
# Create virtual environment
conda create --name cart_player_build -y
conda activate cart_player_build
conda config --env --set subdir osx-64
conda install python=3.9 -y

# Build app
./scripts/osx_build.sh

# Cleanup
conda deactivate
conda env remove --name cart_player_build -y
```

#### Windows

```bash
# Create virtual environment
python -m venv cart_player_build
.\cart_player_build\Scripts\activate

# Build app
.\scripts\build\windows_build.ps1

# Cleanup
deactivate
rmdir cart_player_build
```

## Credits

- [lesserkuma](https://github.com/lesserkuma), creator of [FlashGBX](https://github.com/lesserkuma/FlashGBX) (thank you very much for your hard work).
- [PySimpleGUI](https://www.pysimplegui.org), a cross-plateform UI for python programming.
- [Freepik](https://www.flaticon.com/fr/icones-gratuites/dragon) for the design of the dragon on the app logo.

*Project started on October 22nd, 2022*
