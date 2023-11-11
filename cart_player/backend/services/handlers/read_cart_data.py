import logging
from typing import List, Type

from cart_player.backend.domain.commands import ReadCartDataCommand
from cart_player.backend.domain.dtos import CartInfo as CartInfoDTO
from cart_player.backend.domain.dtos import GameData as GameDataDTO
from cart_player.backend.domain.dtos import GameImage as GameImageDTO
from cart_player.backend.domain.dtos import GameMetadata as GameMetadataDTO
from cart_player.backend.domain.events import CartDataReadEvent
from cart_player.backend.domain.models import CartInfo, GameData, GameImage, GameMetadata
from cart_player.backend.domain.ports import CartFlasher, GameLibrary, Memory
from cart_player.backend.utils.models import GameDataType
from cart_player.core import Broker, Handler, config
from cart_player.core.exceptions import NoCartInCartFlasherException

logger = logging.getLogger(f"{config.LOGGER_NAME}::ReadCartDataHandler")


class ReadCartDataHandler(Handler):
    """Handle event 'ReadCartDataCommand'."""

    def __init__(
        self,
        broker: Broker,
        memory: Memory,
        cart_flasher: CartFlasher,
        game_library: GameLibrary,
    ):
        super().__init__(broker)
        self._memory = memory
        self._cart_flasher = cart_flasher
        self._game_library = game_library

    @property
    def message_type(self) -> Type:
        return ReadCartDataCommand

    def _handle(self, cmd: ReadCartDataCommand):
        try:
            self._handle_command(cmd)
        except Exception as e:
            if cmd.raise_error:
                raise e

            # Publish CartDataReadEvent
            evt = self._build_cart_data_read_event(
                cmd=cmd,
                success=False,
                cart_info=None,
                game_data_list=None,
                game_metadata=None,
                game_image=None,
            )
            self._publish(evt)

            logger.error(f"An exception has occurred: {e}", exc_info=True)

    def _handle_command(self, cmd: ReadCartDataCommand):
        # CartInfo
        if cmd.cart_info:
            cart_info = CartInfo.create(cmd.cart_info)
        else:
            try:
                cart_info: CartInfo = self._cart_flasher.read_cart_info()
            except (NoCartInCartFlasherException, RuntimeError) as e:
                if cmd.raise_error:
                    raise e
                cart_info = None
            else:
                game_data = self._memory.get_by_name(cart_info.cart_filename, GameDataType.CART, True)
                if game_data:
                    cart_info.load_from_bytes(game_data.content)
                else:
                    self._memory.save(cart_info, cart_info.bytes(), GameDataType.CART)

        # Failure case
        if cart_info is None:
            self._publish(CartDataReadEvent(success=False))
            return

        # GameData list
        game_data_list = self._memory.get_all(cart_info) if not cmd.skip_game_data else None

        # GameMetadata
        if cmd.skip_game_metadata:
            game_metadata = None
        else:
            game_metadata_data = self._memory.get_by_name(cart_info.metadata_filename, GameDataType.METADATA, True)
            if game_metadata_data:
                game_metadata = GameMetadata.create_from_bytes(game_metadata_data.content)
            else:
                game_metadata = self._game_library.get_metadata(cart_info)
                if not game_metadata.is_empty():
                    self._memory.save(cart_info, game_metadata.bytes(), GameDataType.METADATA)

        # GameImage
        if cmd.skip_game_image:
            game_image = None
        else:
            game_image_data = self._memory.get_by_name(cart_info.image_filename, GameDataType.IMAGE, True)
            if game_image_data:
                game_image = GameImage(data=game_image_data.content)
            else:
                game_image = self._game_library.get_image(cart_info)
                if game_image.data:
                    self._memory.save(cart_info, game_image.data, GameDataType.IMAGE)

        # Build DTOs
        cart_info_dto = CartInfoDTO(
            title=cart_info.title,
            header_checksum=cart_info.header_checksum,
            support=cart_info.support,
            region=cart_info.region,
            id_override=cart_info.id_override,
            image_ratio_override=cart_info.image_ratio_override,
            save_supported=cart_info.save_supported,
            sgb_supported=cart_info.sgb_supported,
        )
        game_data_dto_list = self._game_data_list_to_dto(game_data_list)
        game_metadata_dto = self._game_metadata_to_dto(game_metadata)
        game_image_dto = self._game_image_to_dto(game_image)

        # Publish CartDataReadEvent
        evt = self._build_cart_data_read_event(
            cmd=cmd,
            success=True,
            cart_info=cart_info_dto,
            game_data_list=game_data_dto_list,
            game_metadata=game_metadata_dto,
            game_image=game_image_dto,
        )
        self._publish(evt)

    @staticmethod
    def _game_data_list_to_dto(game_data_list: List[GameData]) -> List[GameDataDTO]:
        return (
            [
                GameDataDTO(
                    name=game_data.name,
                    date=game_data.date,
                    type=game_data.type,
                    metadata=game_data.metadata,
                )
                for game_data in game_data_list
            ]
            if game_data_list is not None
            else []
        )

    @staticmethod
    def _game_metadata_to_dto(game_metadata: GameMetadata) -> GameMetadataDTO:
        return (
            GameMetadataDTO(
                name=game_metadata.name,
                description=game_metadata.description,
                platform=game_metadata.platform,
                genre=game_metadata.genre,
                developer=game_metadata.developer,
                region=game_metadata.region,
                release=game_metadata.release,
                crc=game_metadata.crc,
            )
            if game_metadata is not None
            else GameMetadataDTO()
        )

    @staticmethod
    def _game_image_to_dto(game_image: GameImage) -> GameImageDTO:
        return GameImageDTO(data=game_image.data) if game_image is not None else GameImageDTO()

    @staticmethod
    def _build_cart_data_read_event(
        cmd: ReadCartDataCommand,
        success: bool,
        cart_info: CartInfoDTO,
        game_data_list: List[GameDataDTO],
        game_metadata: GameMetadataDTO(),
        game_image: GameImageDTO(),
    ) -> CartDataReadEvent:
        return CartDataReadEvent(
            success=success,
            cart_info=cart_info,
            game_data_list=game_data_list if not cmd.skip_game_data else None,
            game_metadata=game_metadata if not cmd.skip_game_metadata else None,
            game_image=game_image if not cmd.skip_game_image else None,
        )
