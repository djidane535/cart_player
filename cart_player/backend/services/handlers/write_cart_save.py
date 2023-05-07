import logging
from datetime import timedelta
from typing import Optional, Type

from cart_player.backend.domain.commands import WriteCartSaveCommand
from cart_player.backend.domain.dtos import CartInfo as CartInfoDTO
from cart_player.backend.domain.events import CartSaveWrittenEvent, WriteCartSaveProgressEvent
from cart_player.backend.domain.models import CartInfo, GameData
from cart_player.backend.domain.ports import CartFlasher, Memory
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Broker, Handler, config
from cart_player.core.exceptions import NoCartInCartFlasherException

logger = logging.getLogger(f"{config.LOGGER_NAME}::WriteCartSaveHandler")


class WriteCartSaveHandler(Handler):
    """Handle event 'WriteCartSaveCommand'."""

    def __init__(self, broker: Broker, memory: Memory, cart_flasher: CartFlasher):
        super().__init__(broker)
        self._memory = memory
        self._cart_flasher = cart_flasher

    @property
    def message_type(self) -> Type:
        return WriteCartSaveCommand

    def _handle(self, cmd: WriteCartSaveCommand):
        try:
            save_data: GameData = self._memory.get_by_name(cmd.save_name, type=GameDataType.SAVE, with_content=True)
            if save_data is None or save_data.content is None:
                raise RuntimeError(f"No save data has been found ({cmd.save_name=})")

            cart_info: CartInfo = self._cart_flasher.read_cart_info()
            self._cart_flasher.write_save(cart_info, save_data.content, self._report_progress)
        except (NoCartInCartFlasherException, RuntimeError) as e:
            logger.error(f"An error occurred when writing save: {e}", exc_info=True)
            self._publish(CartSaveWrittenEvent(success=False))
        else:
            self._publish(
                CartSaveWrittenEvent(
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
        self._publish(WriteCartSaveProgressEvent(current=current, eta=eta))
