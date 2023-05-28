import base64
import glob
import hashlib
import itertools
import json
import logging
import pickle
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional, Tuple, Union

from cart_player.backend.domain.dtos import LocalMemoryConfiguration
from cart_player.backend.domain.models import CartInfo, GameData
from cart_player.backend.domain.ports import Memory
from cart_player.backend.utils.models import GameDataType, GameSupport
from cart_player.core import config

logger = logging.getLogger(f"{config.LOGGER_NAME}::LocalMemory")


class LocalMemory(Memory):
    """Implementation of Memory where data is stored locally

    Args:
        root_path: Path to memory folder.

    Properties:
        root_path: Path to memory folder.
        game_path: Path to game folder within memory folder.
        save_path: Path to save folder within memory folder.
        metadata_path: Path to metadata folder within memory folder.
        image_path: Path to image folder within memory folder.
        pocket_image_path: Path to pocket image folder within memory folder.
    """

    def __init__(self, root_path: Union[Path, str]):
        self._root_path = Path(root_path)

    def configure(self):
        """Configure the memory folders."""
        for support in GameSupport:
            support_subpath = self._get_support_subpath(support)
            (self.cart_path / support_subpath).mkdir(parents=True, exist_ok=True)
            (self.game_path / support_subpath).mkdir(parents=True, exist_ok=True)
            (self.save_path / support_subpath).mkdir(parents=True, exist_ok=True)
            (self.metadata_path / support_subpath).mkdir(parents=True, exist_ok=True)
            (self.image_path / support_subpath).mkdir(parents=True, exist_ok=True)
            (self.pocket_image_path / support_subpath).mkdir(parents=True, exist_ok=True)

    @property
    def root_path(self) -> Path:
        """Path to memory folder."""
        return self._root_path

    @property
    def data_filepath(self) -> Path:
        """Path to file 'data'."""
        filepath = self._root_path / Path("data.json")
        if not filepath.exists():
            filepath.touch()
            filepath.write_text("{}")
        return filepath

    @property
    def cart_path(self) -> Path:
        """Path to memory cart folder."""
        return self._root_path / Path("cart")

    @property
    def game_path(self) -> Path:
        """Path to memory game folder."""
        return self._root_path / Path("game")

    @property
    def save_path(self) -> Path:
        """Path to memory save folder."""
        return self.game_path

    @property
    def metadata_path(self) -> Path:
        """Path to memory metadata folder."""
        return self._root_path / Path("metadata")

    @property
    def image_path(self) -> Path:
        """Path to memory image folder."""
        return self._root_path / Path("image")

    @property
    def pocket_image_path(self) -> Path:
        """Path to memory pocket image folder."""
        return self._root_path / Path("pocket_image")

    def save(self, cart_info: CartInfo, content: bytes, type: GameDataType, metadata: dict = {}):
        """Save game data into local memory, which follows this structure:
            * Cart games location: <root_path>/games/
            * Cart saves location: <root_path>/saves/

        Those paths are built automatically if they do not exist yet.

        Cart games are overwritten if they already exist.
        Cart saves are historized as follows:
          - Current save is renamed with a suffix '.<increment>' where <increment> is an integer.
          - An higher <increment> means the save is more recent.
          - New save takes the place of the current save.

        When saving GameDataType.ANALOGUE_POCKET_IMAGE, key "crc" is required in metadata dict (as a string).

        Args:
            cart_info: Information about the cart whose content has to be saved.
            type: Type of game data.
            metadata: Metadata of the file to save.
                      Required for GameDataType.ANALOGUE_POCKET_IMAGE w/ 'crc' key (str).

        Raises:
            RuntimeError: If an error happens when creating local memory folders or when writing content into a file.
            ValueError: If type == GameDataType.ANALOGUE_POCKET_IMAGE and 'crc' key is missing in metadata.
        """
        if type == GameDataType.ANALOGUE_POCKET_IMAGE and not metadata.get("crc", None):
            raise ValueError(f"Unable to save Analogue Pocket image without a crc (cart_info={cart_info}).")

        filepath = self._get_filepath(cart_info, type, metadata)

        # Process content
        processed_content, is_bytes = LocalMemory._process_content(cart_info, content, filepath)

        # Skip if file already exists
        if LocalMemory._is_file_content_matching(processed_content, is_bytes, filepath):
            logger.warning(
                f"File content is the same, no new file has been created (id={cart_info.id}, filepath={str(filepath)})"
            )
            return

        # Create file parent directory(ies)
        try:
            filepath.parent.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            raise RuntimeError(
                "An error occured when creating missing parent directories " f"({cart_info=}, {filepath=}).",
            ) from e

        # Historize saves
        if type == GameDataType.SAVE and filepath.exists():
            LocalMemory._historize_file(filepath)

        try:
            with open(str(filepath), "wb" if is_bytes else "w") as f:
                f.write(processed_content)
        except Exception as e:
            # Delete file if it has been created
            filepath.unlink(missing_ok=True)

            # Restore initial save in case of error
            if type == GameDataType.SAVE:
                LocalMemory._restore_last_file(filepath)

            raise RuntimeError(
                f"An error occured when writing content into file ({cart_info=}, {filepath=}).",
            ) from e

        # Save metadata
        if metadata:
            data = json.loads(self.data_filepath.read_text())
            md5 = LocalMemory._get_md5(content)
            data[md5] = metadata
            self.data_filepath.write_text(json.dumps(data))

    def get_by_name(self, name: str, type: GameDataType, with_content: bool = False) -> Optional[GameData]:
        path = self._get_path(type)
        files = list(glob.glob(str(path) + "/**/*", recursive=True))
        file = next((Path(_file) for _file in files if Path(_file).is_file() and Path(_file).name == name), None)
        if file is None:
            return None

        date = datetime.fromtimestamp(file.stat().st_mtime)
        if not with_content:
            content = None
        elif type in [GameDataType.CART, GameDataType.METADATA]:
            content = pickle.dumps(json.loads(file.read_text()))
        elif type == GameDataType.IMAGE:
            content = base64.b64encode(file.read_bytes())
        else:
            content = file.read_bytes()

        # Try retrieve metadata
        data = json.loads(self.data_filepath.read_text())
        md5 = LocalMemory._get_md5(content)
        metadata = data.get(md5, None)

        return GameData(name=name, date=date, content=content, type=type, extension=file.suffix, metadata=metadata)

    def get_all(
        self,
        cart_info: CartInfo,
        type: Optional[GameDataType] = None,
        with_content: bool = False,
    ) -> List[GameData]:
        # Call method with all GameDataTypes and concat all results
        if type is None:
            return list(
                itertools.chain(
                    *[
                        self.get_all(cart_info, type, with_content)
                        for type in GameDataType
                        if type != GameDataType.ANALOGUE_POCKET_IMAGE
                    ],
                ),
            )

        path = self._get_path(type)
        file_regex = LocalMemory._build_file_regex(cart_info, type)
        files = [
            Path(_file)
            for _file in glob.glob(str(path) + "/**/*", recursive=True)
            if Path(_file).is_file() and re.match(file_regex, Path(_file).name)
        ]

        # Build list of GameData
        data = json.loads(self.data_filepath.read_text())
        game_data_list = []
        for f in files:
            # Retrieve metadata
            content = (
                pickle.dumps(json.loads(f.read_text()))
                if type in [GameDataType.CART, GameDataType.METADATA]
                else f.read_bytes()
            )
            md5 = LocalMemory._get_md5(content)
            metadata = data.get(md5, None)

            # Add GameData to list
            game_data_list.append(
                GameData(
                    name=f.name,
                    date=datetime.fromtimestamp(f.stat().st_mtime),
                    content=content if with_content else None,
                    type=type,
                    extension=f.suffix,
                    metadata=metadata,
                )
            )

        return game_data_list

    def update_configuration(self, dto: LocalMemoryConfiguration):
        """Update memory configuration.

        Args:
            dto: Local memory configuration.
        """
        self._root_path = dto.root_path

    def _get_filepath(self, cart_info: CartInfo, type: GameDataType, metadata: dict) -> Path:
        """Return the filepath of the file where to save content in memory.

        Args:
            cart_info: Information about the cart whose content has to be saved.
            type: Type of content.
            with_increment: If True, add an incrementing number to avoid erasing pre-existing files.
            metadata: Metadata of the file.

        Return:
            Filepath of the file where to save content in memory.
        """
        return {
            GameDataType.CART: self._get_cart_filepath,
            GameDataType.GAME: self._get_game_filepath,
            GameDataType.SAVE: self._get_base_save_filepath,
            GameDataType.METADATA: self._get_metadata_filepath,
            GameDataType.IMAGE: self._get_image_filepath,
            GameDataType.ANALOGUE_POCKET_IMAGE: lambda cart_info: self._get_pocket_image_filepath(
                cart_info,
                crc=metadata.get("crc", None),
            ),
        }[type](cart_info)

    def _get_cart_filepath(self, cart_info: CartInfo) -> Path:
        """Return the filepath of the file where to save content in memory (game).

        Args:
            cart_info: Information about the cart whose content has to be saved.

        Return:
            Filepath of the file where to save content in memory (game).
        """
        support_subpath = LocalMemory._get_support_subpath(cart_info.support)
        return self.cart_path / support_subpath / Path(f"{cart_info.cart_filename}")

    def _get_game_filepath(self, cart_info: CartInfo) -> Path:
        """Return the filepath of the file where to save content in memory (game).

        Args:
            cart_info: Information about the cart whose content has to be saved.

        Return:
            Filepath of the file where to save content in memory (game).
        """
        support_subpath = LocalMemory._get_support_subpath(cart_info.support)
        return self.game_path / support_subpath / Path(f"{cart_info.game_filename}")

    def _get_base_save_filepath(self, cart_info: CartInfo) -> Path:
        """Return the filepath of the file where to save content in memory (save).

        Args:
            cart_info: Information about the cart whose content has to be saved.

        Return:
            Filepath of the file where to save content in memory (save).
        """
        support_subpath = LocalMemory._get_support_subpath(cart_info.support)
        return self.save_path / support_subpath / Path(f"{cart_info.base_save_filename}")

    def _get_metadata_filepath(self, cart_info: CartInfo) -> Path:
        """Return the filepath of the file where to save content in memory (metadata).

        Args:
            cart_info: Information about the cart whose content has to be saved.

        Return:
            Filepath of the file where to save content in memory (metadata).
        """
        support_subpath = LocalMemory._get_support_subpath(cart_info.support)
        return self.metadata_path / support_subpath / Path(f"{cart_info.metadata_filename}")

    def _get_image_filepath(self, cart_info: CartInfo) -> Path:
        """Return the filepath of the file where to save content in memory (image).

        Args:
            cart_info: Information about the cart whose content has to be saved.

        Return:
            Filepath of the file where to save content in memory (image).
        """
        support_subpath = LocalMemory._get_support_subpath(cart_info.support)
        return self.image_path / support_subpath / Path(f"{cart_info.image_filename}")

    def _get_pocket_image_filepath(self, cart_info: CartInfo, crc: str) -> Path:
        """Return the filepath of the file where to save content in memory (pocket image).

        Args:
            cart_info: Information about the cart whose content has to be saved.
            crc: CRC.

        Return:
            Filepath of the file where to save content in memory (pocket image).
        """
        support_subpath = LocalMemory._get_support_subpath(cart_info.support)
        return self.pocket_image_path / support_subpath / Path(f"{crc}.{cart_info.pocket_image_file_extension}")

    @staticmethod
    def _historize_file(filepath: Path):
        """Historize an existing file with an appropriate incrementing number as suffix.

        Args:
            filepath: Path to the file to historize.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        increment = LocalMemory._get_increment(filepath)
        shutil.move(
            str(filepath),
            str(filepath.with_suffix(filepath.suffix + f".{increment}")),
        )

    @staticmethod
    def _restore_last_file(filepath: Path):
        """Restore the file with its most recent version.

        Args:
            filepath: Path to the file to restore.

        Raises:
            FileNotFoundError: If the file is not historized.
        """
        increment = LocalMemory._get_increment(filepath)
        if increment <= 1:
            raise FileNotFoundError("File is not historized.")
        shutil.move(
            str(filepath.with_suffix(filepath.suffix + f".{increment - 1}")),
            str(filepath),
        )

    @staticmethod
    def _get_increment(filepath: Path) -> Path:
        """Return the incrementing number to add as a suffix to filepath to avoid erasing an existing file.

        Args:
            filepath: Base filepath.

        Returns:
            Incrementing number to add as a suffix to filepath to avoid erasing an existing file.

        Raises:
            FileNotFoundError: If file does not exist.
        """
        increment = 1
        while filepath.with_suffix(filepath.suffix + f".{increment}").exists():
            increment += 1
        return increment

    def _get_path(self, type: GameDataType) -> Path:
        """Return the path corresponding to a type of data.

        Args:
            type: Type of data for which to retrieve the path.

        Returns:
            The path corresponding to a type of data.
        """
        if type == GameDataType.CART:
            return self.cart_path
        if type == GameDataType.GAME:
            return self.game_path
        if type == GameDataType.SAVE:
            return self.save_path
        if type == GameDataType.METADATA:
            return self.metadata_path
        if type == GameDataType.IMAGE:
            return self.image_path
        if type == GameDataType.ANALOGUE_POCKET_IMAGE:
            return self.pocket_image_path

        raise NotImplementedError

    @staticmethod
    def _get_support_subpath(support: GameSupport) -> str:
        return {
            GameSupport.GAMEBOY: Path("Nintendo - Game Boy"),
            GameSupport.GAMEBOY_COLOR: Path("Nintendo - Game Boy Color"),
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: Path("Nintendo - Game Boy Color"),
            GameSupport.GAMEBOY_ADVANCE: Path("Nintendo - Game Boy Advance"),
        }[support]

    @staticmethod
    def _build_file_regex(cart_info: CartInfo, type: GameDataType) -> Path:
        """Return the file regex corresponding to a type of data.

        Args:
            cart_info: Cart metadata for which to build the file regex.
            type: Type of data for which to build the file regex.

        Returns:
            The file regex corresponding to a type of data.
        """
        return {
            GameDataType.CART: f"^{re.escape(cart_info.cart_filename)}$",
            GameDataType.GAME: f"^{re.escape(cart_info.game_filename)}$",
            GameDataType.SAVE: f"^{re.escape(cart_info.base_save_filename)}(.[1-9][0-9]*)?$",
            GameDataType.METADATA: f"^{re.escape(cart_info.metadata_filename)}$",
            GameDataType.IMAGE: f"^{re.escape(cart_info.image_filename)}$",
        }[type]

    @staticmethod
    def _is_file_content_matching(content: bytes, is_bytes: bool, filepath: Path) -> bool:
        """
        Check if a file at `filepath` exists and its content matches `content`.

        Args:
            content (bytes): The expected content of the file.
            is_bytes (bool): True if content is bytes.
            filepath (Path): The path to the file.

        Returns:
            bool: True if the file exists and its content matches `content`, otherwise False.
        """
        if not filepath.is_file():
            return False

        with open(filepath, "rb" if is_bytes else "r") as f:
            file_content = f.read()

        return file_content == content

    @staticmethod
    def _process_content(cart_info: CartInfo, content: bytes, filepath: str) -> Tuple[Any, bool]:
        """
        Process the content of a file based on its type.

        Args:
            cart_info (CartInfo): An object containing information about the cart.
            content (bytes): The content of the file to be processed.
            filepath (str): The path to the file.

        Returns:
            A tuple containing the processed content and a boolean flag indicating
            whether the content is bytes (True) or not (False).

        Raises:
            RuntimeError: If an error occurs while processing the content.
        """
        try:
            if filepath.suffix == ".json":
                return json.dumps(pickle.loads(content)), False
            elif filepath.suffix == ".png":
                return base64.b64decode(content), True
            else:
                return content, True
        except Exception as e:
            raise RuntimeError(
                f"An error occured when processing content ({cart_info=}, {filepath=}).",
            ) from e

    @staticmethod
    def _get_md5(content: Union[dict, bytes]) -> str:
        if isinstance(content, dict):
            content = json.dumps(content).encode()

        return hashlib.md5(content).hexdigest()
