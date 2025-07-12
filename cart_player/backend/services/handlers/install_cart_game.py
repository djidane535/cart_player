import logging
from datetime import timedelta
from typing import Optional, Type

from cart_player.backend.domain.commands import InstallCartGameCommand
from cart_player.backend.domain.dtos import CartInfo as CartInfoDTO
from cart_player.backend.domain.events import CartGameInstalledEvent, InstallCartGameProgressEvent
from cart_player.backend.domain.models import CartInfo
from cart_player.backend.domain.ports import CartFlasher, Memory
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Broker, Handler, config
from cart_player.core.exceptions import NoCartInCartFlasherException

logger = logging.getLogger(f"{config.LOGGER_NAME}::BackupCartSaveHandler")


class InstallCartGameHandler(Handler):
    """Handle event 'InstallCartGameCommand'."""

    def __init__(self, broker: Broker, memory: Memory, cart_flasher: CartFlasher):
        super().__init__(broker)
        self._memory = memory
        self._cart_flasher = cart_flasher

    @property
    def message_type(self) -> Type:
        return InstallCartGameCommand

    def _handle(self, cmd: InstallCartGameCommand):
        try:
            # Check cart has not been swapped meanwhile
            cart_info: CartInfo = self._cart_flasher.read_cart_info()
            if cmd.cart_info.header_checksum != cart_info.header_checksum:
                logger.warning("Another game has been inserted meanwhile. Try again.")
                self._publish(CartGameInstalledEvent(success=False))
                return

            cart_info = CartInfo.create(cmd.cart_info)
            content = self._cart_flasher.read_game(cart_info, self._report_progress)
        except (NoCartInCartFlasherException, RuntimeError) as e:
            logger.error(f"An error occurred when installing game: {e}", exc_info=True)
            self._publish(CartGameInstalledEvent(success=False))
        else:
            self._memory.save(cart_info, content, GameDataType.GAME)
            self._publish(
                CartGameInstalledEvent(success=True, cart_info=cmd.cart_info),
            )

    def _report_progress(self, current: float, eta: Optional[timedelta]):
        self._publish(InstallCartGameProgressEvent(current=current, eta=eta))
