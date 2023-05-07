import glob
import logging
from pathlib import Path
from typing import Optional, Type

from cart_player.backend.domain.commands import BackupSaveFileAfterPlayingCommand
from cart_player.backend.domain.models import CartInfo
from cart_player.backend.domain.ports import Memory
from cart_player.backend.utils.models import GameDataType, SaveDataOrigin
from cart_player.core import Broker, Handler, config

logger = logging.getLogger(f"{config.LOGGER_NAME}::BackupSaveFileAfterPlayingHandler")


class BackupSaveFileAfterPlayingHandler(Handler):
    """Handle event 'BackupSaveFileAfterPlayingCommand'."""

    def __init__(self, broker: Broker, memory: Memory):
        super().__init__(broker)
        self._memory = memory

    @property
    def message_type(self) -> Type:
        return BackupSaveFileAfterPlayingCommand

    def _handle(self, cmd: BackupSaveFileAfterPlayingCommand):
        filenames = glob.glob(str(cmd.target_path / Path("GAME*")))
        game_target_filepath_name = next(iter([fn for fn in filenames if not fn.endswith(".sav")]), None)
        save_target_filepath_name = next(iter([fn for fn in filenames if fn.endswith(".sav")]), None)

        game_target_filepath = (
            (cmd.target_path / Path(game_target_filepath_name)) if game_target_filepath_name else None
        )
        save_target_filepath = (
            (cmd.target_path / Path(save_target_filepath_name)) if save_target_filepath_name else None
        )

        if save_target_filepath and save_target_filepath.exists():
            with open(str(save_target_filepath), "rb") as f:
                content = f.read()
            cart_info = CartInfo.create(cmd.cart_info)
            self._memory.save(cart_info, content, GameDataType.SAVE, metadata={"tag": SaveDataOrigin.EMULATOR})

        self._try_delete(game_target_filepath)
        self._try_delete(save_target_filepath)

    def _try_delete(self, filepath: Optional[Path]):
        if filepath and filepath.exists() and filepath.is_file():
            try:
                filepath.unlink()
            except FileNotFoundError:
                pass
