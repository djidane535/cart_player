import itertools
import os
from collections import defaultdict
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Union

from cart_player.backend.adapters.memory import LocalMemory
from cart_player.backend.domain.models import CartInfo, GameData
from cart_player.backend.utils.models import GameDataType


class MockGameData:
    def __init__(self, cart_info: CartInfo, game_installed: bool = False, n_saves: int = 0):
        self.cart_info = cart_info
        self.game_installed = game_installed
        self.n_saves = n_saves


class MockMemory(LocalMemory):
    def __init__(self, root_path: Union[Path, str], entries: List[MockGameData] = []):
        super().__init__(root_path=root_path)

        self._memory_carts: Dict[str, List[GameData]] = defaultdict(list)
        self._memory_games: Dict[str, List[GameData]] = defaultdict(list)
        self._memory_saves: Dict[str, List[GameData]] = defaultdict(list)
        self._memory_metadata_list: Dict[str, List[GameData]] = defaultdict(list)
        self._memory_images: Dict[str, List[GameData]] = defaultdict(list)

        for entry in entries:
            self._memory_games[entry.cart_info.game_filename] = [
                GameData(
                    name=f"{entry.cart_info.game_filename}",
                    date=datetime.now() - timedelta(minutes=5),
                    content=os.urandom(54),
                    type=GameDataType.GAME,
                )
                if entry.game_installed
                else None
            ]

            if entry.n_saves > 0:
                self._memory_saves[entry.cart_info.base_save_filename] = [
                    GameData(
                        name=f"{entry.cart_info.base_save_filename}",
                        date=datetime.now() - timedelta(minutes=10 * (entry.n_saves - i + 1)),
                        content=os.urandom(17),
                        type=GameDataType.SAVE,
                    )
                    for i in range(
                        entry.n_saves,
                        0,
                        -1,
                    )  # first: entry.n_saves, last: 1
                ]
                for i, save in enumerate(
                    self._memory_saves[entry.cart_info.base_save_filename][-1:0:-1],
                ):
                    save.name += f".{i + 1}"

    def save(self, cart_info: CartInfo, content: bytes, type: GameDataType):
        if type == GameDataType.CART:
            self._memory_carts[cart_info.cart_filename] = [
                GameData(
                    name=f"{cart_info.cart_filename}",
                    date=datetime.now(),
                    content=content,
                    type=GameDataType.CART,
                )
            ]

        if type == GameDataType.GAME:
            self._memory_games[cart_info.game_filename] = [
                GameData(
                    name=f"{cart_info.game_filename}",
                    date=datetime.now(),
                    content=content,
                    type=GameDataType.GAME,
                )
            ]

        if type == GameDataType.SAVE:
            saves = self._memory_saves[cart_info.base_save_filename]
            if saves:
                saves[0].name += f".{len(saves)}"
                saves[0], saves[-1] = saves[-1], saves[0]

            saves.insert(
                0,
                GameData(
                    name=f"{cart_info.base_save_filename}",
                    date=datetime.now(),
                    content=content,
                    type=GameDataType.SAVE,
                ),
            )

        if type == GameDataType.METADATA:
            self._memory_metadata_list[cart_info.metadata_filename] = [
                GameData(
                    name=f"{cart_info.metadata_filename}",
                    date=datetime.now(),
                    content=content,
                    type=GameDataType.METADATA,
                )
            ]

        if type == GameDataType.IMAGE:
            self._memory_metadata_list[cart_info.image_filename] = [
                GameData(
                    name=f"{cart_info.image_filename}",
                    date=datetime.now(),
                    content=content,
                    type=GameDataType.IMAGE,
                )
            ]

    def get_by_name(self, name: str, type: GameDataType, with_content: bool = False) -> Optional[GameData]:
        entry: Optional[GameData] = next(
            (
                entry
                for entry_list in self._get_data_list(type).values()
                for entry in entry_list
                if entry.name == name and entry.type == type
            ),
            None,
        )
        if entry is None:
            return None

        entry = deepcopy(entry)
        entry.content = None if not with_content else entry.content
        return entry

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
                    *[self.get_all(cart_info, type, with_content) for type in GameDataType],
                ),
            )

        if type == GameDataType.CART:
            carts = deepcopy(self._memory_carts[cart_info.cart_filename])
            if not with_content:
                for cart in carts:
                    cart.content = None
            return carts

        if type == GameDataType.GAME:
            games = deepcopy(self._memory_games[cart_info.game_filename])
            if not with_content:
                for game in games:
                    game.content = None
            return games

        if type == GameDataType.SAVE:
            saves = deepcopy(self._memory_saves[cart_info.base_save_filename])
            if not with_content:
                for save in saves:
                    save.content = None

            return saves

        if type == GameDataType.METADATA:
            metadata_list = deepcopy(self._memory_metadata_list[cart_info.metadata_filename])
            if not with_content:
                for metadata in metadata_list:
                    metadata.content = None
            return metadata_list

        if type == GameDataType.IMAGE:
            images = deepcopy(self._memory_images[cart_info.image_filename])
            if not with_content:
                for image in images:
                    image.content = None
            return images

    def _get_data_list(self, type: GameDataType) -> Dict[str, GameData]:
        if type == GameDataType.CART:
            return self._memory_carts
        if type == GameDataType.GAME:
            return self._memory_games
        if type == GameDataType.SAVE:
            return self._memory_saves
        if type == GameDataType.METADATA:
            return self._memory_metadata_list
        if type == GameDataType.IMAGE:
            return self._memory_images
