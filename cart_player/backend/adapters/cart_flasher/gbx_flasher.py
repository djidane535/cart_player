import glob
import logging
import os
import re
import tempfile
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Callable, Optional

from cart_player.backend import config
from cart_player.backend.domain.dtos import CartInfo as CartInfoDTO
from cart_player.backend.domain.models import CartInfo
from cart_player.backend.domain.ports import CartFlasher
from cart_player.backend.utils.models import GameSupport

from .utils import get_name, get_region, run_command_with_realtime_output

logger = logging.getLogger(f"{config.LOGGER_NAME}::GBXFlasher")


# Success messages
ROM_BACKUP_VERIFIED = "The ROM backup is complete and the checksum was verified successfully!"
SAVE_BACKUP_VERIFIED = "The save data backup is complete!"
SAVE_ERASE_COMPLETED = "The save data was erased."
SAVE_UPLOAD_COMPLETED = "The save data was restored!"
SUCCESS_MESSAGES = [ROM_BACKUP_VERIFIED, SAVE_BACKUP_VERIFIED, SAVE_ERASE_COMPLETED, SAVE_UPLOAD_COMPLETED]

# Success values
SUPER_GAME_BOY_SUPPORTED = "Supported"

# Failure values
INVALID_HEADER_CHECKSUM = "Invalid"
NONE_SAVE_TYPE = "None"

# Other values
GAMEBOY_COLOR_NO_SUPPORT = "No support"
GAMEBOY_COLOR_SUPPORTED = "Supported"
GAMEBOY_COLOR_REQUIRED = "Required"

# Cart info keys
GAME_TITLE = "Game Title"
GAME_CODE = "Game Code"
GAME_BOY_COLOR = "Game Boy Color"
HEADER_CHECKSUM = "Header Checksum"
SAVE_TYPE = "Save Type"
SUPER_GAME_BOY = "Super Game Boy"


class GBXFlasherMode(str, Enum):
    DMG = "dmg"
    AGB = "agb"


class GBXFlasher(CartFlasher):
    """Cart flasher, allowing to interact with real carts using a GBxCart.

    Properties:
        cart_inserted: True if a cart is inserted.
        is_busy: True if cart flasher is not available.
    """

    last_command_success: bool = False

    @property
    def cart_inserted(self) -> bool:
        return True  # cannot determine if cart is inserted or not, so we assume it is always the case

    def _read_cart_info(self) -> CartInfo:
        # Fill up CartInfoDTO
        dto = None
        for mode in GBXFlasherMode:
            exceptions = []
            dto = CartInfoDTO(support=GameSupport.GAMEBOY_ADVANCE if mode == GBXFlasherMode.AGB else None)
            flashgbx_path = self.__get_flashgbx_path()
            command = f"{flashgbx_path} --mode {mode} --action info"
            try:
                GBXFlasher.last_command_success = False
                run_command_with_realtime_output(command, lambda line: self.__read_cart_info_handler(mode, dto, line))
            except RuntimeError as e:
                dto = None
                exceptions.append((mode, e))
            else:
                if GBXFlasher.last_command_success:
                    break

        # Error cases
        if not GBXFlasher.last_command_success:
            raise RuntimeError(f"Command '{command}' has failed.")
        if not dto:
            raise RuntimeError("\n".join(f"[{mode}]: {type(e)} >> {e}" for mode, e in exceptions))

        # Add in id and region
        dto.id_override = get_name(dto.title, dto.code, dto.header_checksum, dto.support)
        dto.region = get_region(dto.id)

        logger.debug(f"Bash command(s) result(s): {dto=}")

        return CartInfo.create(dto)

    def _read_game(
        self, cart_info: CartInfo, report_progress_callback: Callable[[float, Optional[timedelta]], None]
    ) -> bytes:
        mode = GBXFlasherMode.AGB if cart_info.support == GameSupport.GAMEBOY_ADVANCE else GBXFlasherMode.DMG

        # Get a temporary filepath
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        os.unlink(f.name)
        filepath = Path(f.name)

        flashgbx_path = self.__get_flashgbx_path()
        command = f"{flashgbx_path} --mode {mode} --action backup-rom {filepath}"
        GBXFlasher.last_command_success = False
        run_command_with_realtime_output(command, lambda line: self.__read_game_handler(report_progress_callback, line))
        if not GBXFlasher.last_command_success:
            raise RuntimeError(f"Command '{command}' has failed.")

        with open(filepath, "rb") as f:
            return f.read()

    def _read_save(
        self, cart_info: CartInfo, report_progress_callback: Callable[[float, Optional[timedelta]], None]
    ) -> bytes:
        mode = GBXFlasherMode.AGB if cart_info.support == GameSupport.GAMEBOY_ADVANCE else GBXFlasherMode.DMG

        # Get a temporary filepath
        f = tempfile.NamedTemporaryFile(delete=False)
        f.close()
        os.unlink(f.name)
        filepath = Path(f.name)

        flashgbx_path = self.__get_flashgbx_path()
        command = f"{flashgbx_path} --mode {mode} --action backup-save {filepath}"
        GBXFlasher.last_command_success = False
        run_command_with_realtime_output(command, lambda line: self.__read_save_handler(report_progress_callback, line))
        if not GBXFlasher.last_command_success:
            raise RuntimeError(f"Command '{command}' has failed.")

        with open(filepath, "rb") as f:
            data = f.read()
        os.remove(f.name)
        return data

    def _erase_save(
        self, cart_info: CartInfo, report_progress_callback: Callable[[float, Optional[timedelta]], None]
    ) -> bytes:
        mode = GBXFlasherMode.AGB if cart_info.support == GameSupport.GAMEBOY_ADVANCE else GBXFlasherMode.DMG

        flashgbx_path = self.__get_flashgbx_path()
        command = f"{flashgbx_path} --mode {mode} --action erase-save --overwrite"
        GBXFlasher.last_command_success = False
        run_command_with_realtime_output(
            command, lambda line: self.__erase_save_handler(report_progress_callback, line)
        )
        if not GBXFlasher.last_command_success:
            raise RuntimeError(f"Command '{command}' has failed.")

    def _write_save(
        self, cart_info: CartInfo, data: bytes, report_progress_callback: Callable[[float, Optional[timedelta]], None]
    ):
        mode = GBXFlasherMode.AGB if cart_info.support == GameSupport.GAMEBOY_ADVANCE else GBXFlasherMode.DMG

        # Save data into a temporary filepath
        f = tempfile.NamedTemporaryFile(delete=False)
        with open(f.name, "wb") as f:
            f.write(data)
        filepath = Path(f.name)

        flashgbx_path = self.__get_flashgbx_path()
        command = f"{flashgbx_path} --mode {mode} --action restore-save {filepath} --overwrite"
        GBXFlasher.last_command_success = False
        run_command_with_realtime_output(
            command, lambda line: self.__write_save_handler(report_progress_callback, line)
        )

        os.remove(f.name)
        if not GBXFlasher.last_command_success:
            raise RuntimeError(f"Command '{command}' has failed.")

    @classmethod
    def __check_if_success_message_received(cls, line: str):
        if any(success_message in line for success_message in SUCCESS_MESSAGES):
            message = line.split(".")[0] + "."
            message = re.sub(r"\033\[[0-9;]*m", "", message)  # remove ANSI colour
            return True
        return False

    @classmethod
    def __read_cart_info_handler(cls, mode: GBXFlasherMode, dto: CartInfoDTO, line: str):
        try:
            if line.startswith(GAME_TITLE):
                dto.title = re.search(fr"{GAME_TITLE}:\s+(.+)", line).group(1).strip()
            if line.startswith(GAME_CODE):
                dto.code = re.search(fr"{GAME_CODE}:\s+(.+)", line).group(1).strip()
            if mode == GBXFlasherMode.DMG and line.startswith(GAME_BOY_COLOR):
                gamboy_color_support_str = re.search(fr"{GAME_BOY_COLOR}:\s+(.+)", line).group(1).strip()
                dto.support = cls.__to_support(gamboy_color_support_str)
            if line.startswith(HEADER_CHECKSUM):
                if INVALID_HEADER_CHECKSUM not in line:
                    dto.header_checksum = re.search(r"(?<=0x)[0-9A-Fa-f]+", line).group().strip()
                    cls.last_command_success = True
            if line.startswith(SAVE_TYPE):
                dto.save_supported = re.search(fr"{SAVE_TYPE}:\s+(.+)", line).group(1).strip() != NONE_SAVE_TYPE
            if mode == GBXFlasherMode.DMG and line.startswith(SUPER_GAME_BOY):
                dto.sgb_supported = (
                    re.search(fr"{SUPER_GAME_BOY}:\s+(.+)", line).group(1).strip() == SUPER_GAME_BOY_SUPPORTED
                )

        except AttributeError:
            pass

    @classmethod
    def __to_support(cls, gamboy_color_support_str: str) -> GameSupport:
        if GAMEBOY_COLOR_NO_SUPPORT in gamboy_color_support_str:
            return GameSupport.GAMEBOY
        elif GAMEBOY_COLOR_SUPPORTED in gamboy_color_support_str:
            return GameSupport.GAMEBOY_OR_GAMEBOY_COLOR
        elif GAMEBOY_COLOR_REQUIRED in gamboy_color_support_str:
            return GameSupport.GAMEBOY_COLOR
        return GameSupport.GAMEBOY

    @classmethod
    def __read_game_handler(cls, callback: Callable[[float, Optional[timedelta]], None], line: str):
        if cls.__check_if_success_message_received(line):
            cls.last_command_success = True
            return

        if "%" in line:
            current = max(0, min(100, int(re.search(r"\d+%", line).group()[:-1]))) / 100.0
            eta = GBXFlasher.__get_eta(line)
            callback(current, eta)
        if ROM_BACKUP_VERIFIED in line:
            callback(1.0, None)

    @classmethod
    def __read_save_handler(cls, callback: Callable[[float, Optional[timedelta]], None], line: str):
        if cls.__check_if_success_message_received(line):
            cls.last_command_success = True
            return

        if "%" in line:
            current = max(0, min(100, int(re.search(r"\d+%", line).group()[:-1]))) / 100.0
            eta = GBXFlasher.__get_eta(line)
            callback(current, eta)
        if SAVE_BACKUP_VERIFIED in line:
            callback(1.0, None)

    @classmethod
    def __erase_save_handler(cls, callback: Callable[[float, Optional[timedelta]], None], line: str):
        if cls.__check_if_success_message_received(line):
            cls.last_command_success = True
            return

        if "%" in line:
            current = max(0, min(100, int(re.search(r"\d+%", line).group()[:-1]))) / 100.0
            eta = GBXFlasher.__get_eta(line)
            callback(current, eta)
        if SAVE_ERASE_COMPLETED in line:
            callback(1.0, None)

    @classmethod
    def __write_save_handler(cls, callback: Callable[[float, Optional[timedelta]], None], line: str):
        if cls.__check_if_success_message_received(line):
            cls.last_command_success = True
            return

        if "%" in line:
            current = max(0, min(100, int(re.search(r"\d+%", line).group()[:-1]))) / 100.0
            eta = GBXFlasher.__get_eta(line)
            callback(current, eta)
        if SAVE_UPLOAD_COMPLETED in line:
            callback(1.0, None)

    @classmethod
    def __get_eta(cls, line: str) -> Optional[timedelta]:
        if "ETA" not in line:
            return None
        eta_str = line.split("ETA")[1].strip()
        try:
            eta = datetime.strptime(eta_str, "%H:%M:%S") - datetime.strptime("00:00:00", "%H:%M:%S")
        except Exception as e:
            logger.info(f"Unable to parse ETA ({line=}): {e}", exc_info=True)
            return None
        return eta

    def __get_flashgbx_path(self) -> str:
        # FlashGBX path
        if os.name == 'nt':  # for Windows
            return "FlashGBX.exe"
        elif os.name == 'posix':  # for macOS and Linux
            # Look for the flashgbx executable
            home_dir = os.path.expanduser("~")
            python_dirs = glob.glob(os.path.join(home_dir, "Library", "Python", "*", "bin"))
            for python_dir in python_dirs:
                flashgbx_path = os.path.join(python_dir, "flashgbx")
                if os.path.exists(flashgbx_path):
                    return flashgbx_path

            # Didn't find the flashgbx executable in any Python directory
            logger.error("FlashGBX not found")
            return ""

        else:
            logger.error("Unsupported operating system")
            return ""
