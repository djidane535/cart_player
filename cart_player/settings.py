import argparse
import os
import sys
from pathlib import Path

from easysettings import EasySettings

APP_NAME = "CartPlayer"
if os.name == 'posix':
    import appdirs

    BASE_APP_PATH = Path(appdirs.user_data_dir(APP_NAME))
else:
    BASE_APP_PATH = Path("./").resolve()

SETTINGS_FILEPATH = BASE_APP_PATH
SETTINGS_FILEPATH = SETTINGS_FILEPATH / "settings.conf"

SETTINGS_MEMORY_PATH = "memory_path"
SETTINGS_USE_MEMORY_MOCK = "use_memory_mock"
SETTINGS_NO_MEMORY = "no_memory"
SETTINGS_USE_CART_FLASHER_MOCK = "use_cart_flasher_mock"
SETTINGS_USE_METADATA_LIBRARIES_MOCK = "use_metadata_libraries_mock"
SETTINGS_USE_IMAGE_LIBRARIES_MOCK = "use_image_libraries_mock"
SETTINGS_RESET_MEMORY = "reset_memory"
SETTINGS_LOGGING_LEVEL = "logging_level"


# Load settings from file
SETTINGS_FILEPATH.parent.mkdir(parents=True, exist_ok=True)
SETTINGS_FILEPATH = str(SETTINGS_FILEPATH)
settings = EasySettings(SETTINGS_FILEPATH)
settings.set(SETTINGS_MEMORY_PATH, settings.get(SETTINGS_MEMORY_PATH))
settings.save()

# Load CLI settings
if "child" in sys.argv[0]:  # pyinstaller build case

    class DefaultCLISettings:
        def __init__(self):
            self.use_mock = False
            self.use_cart_flasher_mock = False
            self.reset_memory = False

    __cli_settings = DefaultCLISettings()
else:  # standard CLI call
    __parser = argparse.ArgumentParser("cart_player")
    __parser.add_argument("--use_mock", action="store_true", help="Use mock adapters")
    __parser.add_argument("--no_memory", action="store_true", help="Disable memory")
    __parser.add_argument("--use_cart_flasher_mock", action="store_true", help="Use mock adapter for cart flasher")
    __parser.add_argument("--reset_memory", action="store_true", help="Reset memory")
    __cli_settings = __parser.parse_args()

cli_settings = {
    SETTINGS_USE_MEMORY_MOCK: __cli_settings.use_mock,
    SETTINGS_NO_MEMORY: __cli_settings.no_memory,
    SETTINGS_USE_CART_FLASHER_MOCK: __cli_settings.use_mock or __cli_settings.use_cart_flasher_mock,
    SETTINGS_USE_METADATA_LIBRARIES_MOCK: __cli_settings.use_mock,
    SETTINGS_USE_IMAGE_LIBRARIES_MOCK: __cli_settings.use_mock,
    SETTINGS_RESET_MEMORY: not __cli_settings.use_mock and __cli_settings.reset_memory,
}
