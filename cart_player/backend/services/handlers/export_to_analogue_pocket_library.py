import logging
from typing import Type

from cart_player.backend.domain.commands import ExportToAnaloguePocketLibraryCommand
from cart_player.backend.domain.models import CartInfo, GameImage
from cart_player.backend.domain.ports import Memory
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Broker, Handler, config

logger = logging.getLogger(f"{config.LOGGER_NAME}::ExportToAnaloguePocketLibraryHandler")


class ExportToAnaloguePocketLibraryHandler(Handler):
    """Handle event 'ExportToAnaloguePocketLibraryCommand'."""

    def __init__(self, broker: Broker, memory: Memory):
        super().__init__(broker)
        self._memory = memory

    @property
    def message_type(self) -> Type:
        return ExportToAnaloguePocketLibraryCommand

    def _handle(self, cmd: ExportToAnaloguePocketLibraryCommand):
        if not cmd.game_metadata.crc:
            logger.error("CRC is required for export.", exc_info=True)
            return
        if not cmd.game_image.data:
            logger.error("No data in the provided game image.", exc_info=True)
            return

        cart_info = CartInfo.create(cmd.cart_info)
        n_data = GameImage.convert_to_analogue_pocket_library(cmd.game_image.data)
        self._memory.save(cart_info, n_data, GameDataType.ANALOGUE_POCKET_IMAGE, {"crc": cmd.game_metadata.crc})
