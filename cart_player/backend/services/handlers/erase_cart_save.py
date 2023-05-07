import logging
from datetime import timedelta
from typing import Optional, Type

from cart_player.backend.domain.commands import EraseCartSaveCommand
from cart_player.backend.domain.dtos import CartInfo as CartInfoDTO
from cart_player.backend.domain.events import CartSaveErasedEvent, EraseCartSaveProgressEvent
from cart_player.backend.domain.models import CartInfo
from cart_player.backend.domain.ports import CartFlasher, Memory
from cart_player.core import Broker, Handler, config
from cart_player.core.exceptions import NoCartInCartFlasherException

logger = logging.getLogger(f"{config.LOGGER_NAME}::EraseCartSaveHandler")


class EraseCartSaveHandler(Handler):
    """Handle event 'EraseCartSaveCommand'."""

    def __init__(self, broker: Broker, memory: Memory, cart_flasher: CartFlasher):
        super().__init__(broker)
        self._memory = memory
        self._cart_flasher = cart_flasher

    @property
    def message_type(self) -> Type:
        return EraseCartSaveCommand

    def _handle(self, cmd: EraseCartSaveCommand):
        try:
            cart_info: CartInfo = self._cart_flasher.read_cart_info()
            self._cart_flasher.erase_save(cart_info, self._report_progress)
        except (NoCartInCartFlasherException, RuntimeError) as e:
            logger.error(f"An error occurred when erasing save: {e}", exc_info=True)
            self._publish(CartSaveErasedEvent(success=False))
        else:
            self._publish(
                CartSaveErasedEvent(  # TODO
                    success=True,
                    cart_info=CartInfoDTO(
                        title=cart_info.title,
                        header_checksum=cart_info.header_checksum,
                        support=cart_info.support,
                        region=cart_info.region,
                        id_override=cart_info.id_override,
                        save_supported=cart_info.save_supported,
                        sgb_supported=cart_info.sgb_supported,
                    ),
                ),
            )

    def _report_progress(self, current: float, eta: Optional[timedelta]):
        self._publish(EraseCartSaveProgressEvent(current=current, eta=eta))
