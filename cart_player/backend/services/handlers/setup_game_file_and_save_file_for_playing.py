import logging
from pathlib import Path
from typing import Type

from cart_player.backend.domain.commands import SetupGameFileAndSaveFileForPlayingCommand
from cart_player.backend.domain.ports import Memory
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Broker, Handler, config
from cart_player.core.utils import open_folder

logger = logging.getLogger(f"{config.LOGGER_NAME}::SetupGameFileAndSaveFileForPlayingHandler")


class SetupGameFileAndSaveFileForPlayingHandler(Handler):
    """Handle event 'SetupGameFileAndSaveFileForPlayingCommand'."""

    def __init__(self, broker: Broker, memory: Memory):
        super().__init__(broker)
        self._memory = memory

    @property
    def message_type(self) -> Type:
        return SetupGameFileAndSaveFileForPlayingCommand

    def _handle(self, cmd: SetupGameFileAndSaveFileForPlayingCommand):
        self._setup(cmd.game_name, GameDataType.GAME, cmd.target_path)
        self._setup(cmd.save_name, GameDataType.SAVE, cmd.target_path)
        open_folder(cmd.target_path)

    def _setup(self, game_data_name: str, game_data_type: GameDataType, target_path: Path):
        if not game_data_name:
            return

        target_path.mkdir(parents=True, exist_ok=True)
        game_data = self._memory.get_by_name(game_data_name, game_data_type, with_content=True)
        target_filepath = target_path / ("GAME" + game_data.extension)
        self._try_delete(target_filepath)

        if game_data and game_data.content:
            with open(str(target_filepath), "wb") as f:
                f.write(game_data.content)

    def _try_delete(self, filepath: Path):
        if filepath.exists() and filepath.is_file():
            try:
                filepath.unlink()
            except FileNotFoundError:
                pass
