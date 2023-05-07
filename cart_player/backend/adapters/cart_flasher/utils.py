import json
import logging
import os
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Callable, Optional

from cart_player.backend import config
from cart_player.backend.resources import MD5_FOLDER_PATH, NOINTRO_FOLDER_PATH
from cart_player.backend.utils.models import GameRegion, GameSupport

logger = logging.getLogger(f"{config.LOGGER_NAME}::bash")


def run_command_with_realtime_output(command: str, handler: Callable[[str], None]) -> bool:
    """Runs the given command as a subprocess and calls the given handler
    function with each line of the subprocess's output in real time.

    Args:
        command: The command to run as a subprocess.
        handler: The function to call with each line of the subprocess's output.

    Returns:
        True if the subprocess completed successfully, False otherwise.
    """
    if os.name == 'nt':  # for Windows
        import subprocess

        # Start the subprocess and redirect its standard input and output streams
        try:
            logger.debug(command)
            process = subprocess.Popen(
                command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, universal_newlines=True
            )
        except subprocess.SubprocessError as e:
            logger.error(f"Failed to start subprocess: {e}", exc_info=True)
            return False

        # Loop until the subprocess has finished running
        while process.poll() is None:
            if not process_data(process, handler):
                return False
        return True

    elif os.name == 'posix':  # for macOS and Linux
        import pexpect

        # Start the subprocess and redirect its standard input and output streams
        try:
            logger.debug(command)
            command_args = command.split(" ")
            child = pexpect.spawn(
                "arch -arm64 " + " ".join(command_args), encoding="utf-8", timeout=10
            )  # TODO detect real arch automatically (difficult under rosetta2)
        except pexpect.ExceptionPexpect as e:
            logger.error(f"Failed to start subprocess: {e}", exc_info=True)
            return False

        # Loop until the subprocess has finished running
        while child.isalive():
            if not process_data(child, handler):
                return False
        return True

    else:
        raise RuntimeError("Unsupported operating system")


def process_data(process, handler):
    """Processes the data from the subprocess.

    Args:
        process: The subprocess object.
        handler: The function to call with each line of the subprocess's output.

    Returns:
        True if the data was processed successfully, False otherwise.
    """
    if os.name == 'nt':  # for Windows
        # Read a line from the subprocess's standard output stream
        try:
            line = process.stdout.readline()
            if not line:
                return True
        except UnicodeDecodeError:
            logger.error("Error decoding subprocess output: {e}", exc_info=True)
            return False

        # Call the handler function with the received data
        logger.debug(line.strip())
        handler(line.strip())
        return True

    elif os.name == 'posix':  # for macOS and Linux
        import pexpect

        # Expect a newline in the subprocess's output
        try:
            process.expect("\r|\n")
        except pexpect.TIMEOUT:
            logger.error("Subprocess timed out: {e}", exc_info=True)
            return False
        except pexpect.EOF:
            return True

        # Call the handler function with the received data
        data = process.before.strip()
        if data:
            logger.debug(data)
            handler(data)
        return True

    else:
        raise RuntimeError("Unsupported operating system")


def get_name(title: str, code: str, header_checksum: str, support: GameSupport) -> str:
    # Get md5
    md5 = get_md5(title, code, header_checksum, support)
    if not md5:
        return None

    # Determine which files to use for retrieving nointro info
    filename = {
        GameSupport.GAMEBOY: "Nintendo - Game Boy",
        GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: "Nintendo - Game Boy Color",
        GameSupport.GAMEBOY_COLOR: "Nintendo - Game Boy Color",
        GameSupport.GAMEBOY_ADVANCE: "Nintendo - Game Boy Advance",
    }[support]
    nointro_filepath = NOINTRO_FOLDER_PATH / Path(f"{filename}.xml")

    # Parse the nointro file and extract name
    tree = ET.parse(nointro_filepath)
    root = tree.getroot()
    entry = root.find(".//rom[@md5='{}']".format(md5))
    rom_name = entry.get("name")
    name = Path(rom_name).stem if rom_name else None

    return name


def get_md5(title: str, code: Optional[str], header_checksum: str, support: GameSupport) -> str:
    # Determine which files to use for retrieving md5
    filename = {
        GameSupport.GAMEBOY: "Nintendo - Game Boy",
        GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: "Nintendo - Game Boy Color",
        GameSupport.GAMEBOY_COLOR: "Nintendo - Game Boy Color",
        GameSupport.GAMEBOY_ADVANCE: "Nintendo - Game Boy Advance",
    }[support]
    md5_filepath = MD5_FOLDER_PATH / Path(f"{filename}.json")

    # Parse the md5 file and extract md5
    with open(md5_filepath, "r") as file:
        md5_references = json.load(file)
    key = next(
        (
            k
            for k in md5_references.keys()
            if k.startswith(title) and (not code or code in k) and k.endswith(header_checksum)
        ),
        None,
    )
    md5 = md5_references.get(key, None)

    # Retry without code if it failed
    if code and not md5:
        return get_md5(title, None, header_checksum, support)

    return md5


def get_region(name: Optional[str]) -> GameRegion:
    if name is None:
        return GameRegion.UNKNOWN
    if "Europe" in name and "USA" in name:
        return GameRegion.EUROPE_OR_USA
    if "Europe" in name and "Australia" in name:
        return GameRegion.EUROPE_OR_AUSTRALIA
    if "World" in name:
        return GameRegion.WORLD
    if "Europe" in name:
        return GameRegion.EUROPE
    if "USA" in name:
        return GameRegion.USA
    if "Australia" in name:
        return GameRegion.AUSTRALIA
    if "Japan" in name:
        return GameRegion.JAPAN
    return GameRegion.UNKNOWN
