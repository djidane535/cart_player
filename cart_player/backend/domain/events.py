from typing import List, Optional

from pydantic import root_validator

from cart_player.backend.domain.dtos import CartInfo, GameData, GameImage, GameMetadata, LocalMemoryConfiguration
from cart_player.core.domain.events import ProgressEvent
from cart_player.core.domain.messages import BaseMessage


class CartOperationStatusEvent(BaseMessage):
    success: bool
    cart_info: Optional[CartInfo] = None

    @root_validator
    def success_without_cart_info(cls, values):
        if values["success"] and not values.get("cart_info", None):
            raise ValueError("Cannot be a success without cart_info.")
        return values

    @root_validator
    def failure_with_cart_info(cls, values):
        if not values["success"] and values.get("cart_info", None):
            raise ValueError("Cannot be a failure with cart_info.")
        return values


class InstallCartGameProgressEvent(ProgressEvent):
    pass


class CartGameInstalledEvent(BaseMessage):
    success: bool
    cart_info: Optional[CartInfo] = None

    @root_validator
    def success_without_cart_info(cls, values):
        if values["success"] and not values.get("cart_info", None):
            raise ValueError("Cannot be a success without cart_info.")
        return values

    @root_validator
    def failure_with_cart_info(cls, values):
        if not values["success"] and values.get("cart_info", None):
            raise ValueError("Cannot be a failure with cart_info.")
        return values


class BackupCartSaveProgressEvent(ProgressEvent):
    pass


class CartSaveBackupEvent(CartOperationStatusEvent):
    pass


class EraseCartSaveProgressEvent(ProgressEvent):
    pass


class CartSaveErasedEvent(CartOperationStatusEvent):
    pass


class WriteCartSaveProgressEvent(ProgressEvent):
    pass


class CartSaveWrittenEvent(CartOperationStatusEvent):
    pass


class CartDataReadEvent(CartOperationStatusEvent):
    game_data_list: Optional[List[GameData]] = None
    game_metadata: Optional[GameMetadata] = None
    game_image: Optional[GameImage] = None

    @root_validator
    def failure_with_game_data_list(cls, values):
        if not values["success"] and values.get("game_data_list", None):
            raise ValueError("Cannot be a failure with game_data_list.")
        return values

    @root_validator
    def failure_with_game_metadata(cls, values):
        if not values["success"] and values.get("game_metadata", None):
            raise ValueError("Cannot be a failure with game_metadata.")
        return values

    @root_validator
    def failure_with_game_image(cls, values):
        if not values["success"] and values.get("game_image", None):
            raise ValueError("Cannot be a failure with game_image.")
        return values


class LocalMemoryConfigurationUpdatedEvent(BaseMessage):
    new_memory_configuration: LocalMemoryConfiguration
