from __future__ import annotations

import abc
import logging
from pathlib import Path
from typing import Optional

from cart_player.backend.api.dtos import CartInfo
from cart_player.backend.utils.models import GBXFlasherMode
from cart_player.core.domain.messages import BaseMessage
from cart_player.frontend import config
from cart_player.frontend.utils.models import EditWindowType

logger = logging.getLogger(f"{config.LOGGER_NAME}::Event")


class Event(BaseMessage):
    pass


class BackupButtonPressedEvent(BaseMessage):
    cart_info: CartInfo

    @staticmethod
    def create(cart_info: CartInfo) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return BackupButtonPressedEvent(cart_info=cart_info)


class DataSelectorButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return DataSelectorButtonPressedEvent()

class EditApplyButtonPressed(BaseMessage):
    edit_type: EditWindowType
    value: str
    cart_info: Optional[CartInfo]

    @property
    def has_value(self) -> bool:
        return bool(self.value)

    @property
    def text(self) -> str:
        return str(self.value)

    @property
    def image_path(self) -> Path:
        return Path(self.value)

    @staticmethod
    def create(edit_type: EditWindowType, value: str, cart_info: Optional[CartInfo]) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditApplyButtonPressed(edit_type=edit_type, value=value, cart_info=cart_info)
    
class EditClearButtonPressed(BaseMessage):
    edit_type: EditWindowType
    cart_info: Optional[CartInfo]

    @staticmethod
    def create(edit_type: EditWindowType, cart_info: Optional[CartInfo]) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditClearButtonPressed(edit_type=edit_type, cart_info=cart_info)

class EditEvent(BaseMessage):
    @property
    @abc.abstractmethod
    def type(self) -> EditWindowType:
        pass

class EditGameCartBoxImageEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_BOX_IMAGE

    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameCartBoxImageEvent()

class EditGameNameEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_NAME
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameNameEvent()


class EditGameDescriptionEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_DESCRIPTION
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameDescriptionEvent()


class EditGamePlatformEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_PLATFORM
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGamePlatformEvent()


class EditGameGenreEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_GENRE
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameGenreEvent()


class EditGameDeveloperEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_DEVELOPER
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameDeveloperEvent()


class EditGameRegionEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_REGION
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameRegionEvent()


class EditGameReleaseEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_RELEASE
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameReleaseEvent()


class EditGameCRCEvent(EditEvent):
    @property
    def type(self) -> EditWindowType:
        return EditWindowType.GAME_CRC
    
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EditGameCRCEvent()

class EraseButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EraseButtonPressedEvent()


class EndSessionButtonPressedEvent(BaseMessage):
    play_window_is_closing: bool
    cart_info: Optional[CartInfo]
    game_session_path: Path

    @staticmethod
    def create(play_window_is_closing: bool, cart_info: CartInfo, game_session_path: Path) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EndSessionButtonPressedEvent(
            play_window_is_closing=play_window_is_closing,
            cart_info=cart_info,
            game_session_path=game_session_path,
        )
    

class InputMemoryFolderButtonPressedEvent(BaseMessage):
    path_str: str

    @staticmethod
    def create(path_str: str) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return InputMemoryFolderButtonPressedEvent(path_str=path_str)

class ComboGBXFlasherPreferredModeUpdated(BaseMessage):
    mode: GBXFlasherMode

    @staticmethod
    def create(mode: GBXFlasherMode) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return ComboGBXFlasherPreferredModeUpdated(mode=mode)

class InstallButtonPressedEvent(BaseMessage):
    cart_info: CartInfo

    @staticmethod
    def create(cart_info: CartInfo) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return InstallButtonPressedEvent(cart_info=cart_info)


class LaunchButtonPressedEvent(BaseMessage):
    game_name: str
    save_name: Optional[str] = None
    game_session_path: Path = None

    @staticmethod
    def create(game_name: str, save_name: str, game_session_path: Path) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return LaunchButtonPressedEvent(game_name=game_name, save_name=save_name, game_session_path=game_session_path)


class OpenMemoryButtonPressedEvent(BaseMessage):
    memory_path: Path

    @staticmethod
    def create(memory_path: Path) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return OpenMemoryButtonPressedEvent(memory_path=memory_path)


class PlaySelectorButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return PlaySelectorButtonPressedEvent()


class PopUpWindowIsClosingEvent(BaseMessage):
    play_window_is_closing: bool
    cart_info: Optional[CartInfo]
    game_session_path: Path

    @staticmethod
    def create(play_window_is_closing: bool, cart_info: CartInfo, game_session_path: Path) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return PopUpWindowIsClosingEvent(
            play_window_is_closing=play_window_is_closing,
            cart_info=cart_info,
            game_session_path=game_session_path,
        )


class RefreshButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return RefreshButtonPressedEvent()


class SettingsSelectorButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return SettingsSelectorButtonPressedEvent()


class UploadButtonPressedEvent(BaseMessage):
    save_name: str

    @staticmethod
    def create(save_name: str) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return UploadButtonPressedEvent(save_name=save_name)


class WindowReadNoWindowEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return WindowReadNoWindowEvent()


class WindowReadTimeoutEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return WindowReadTimeoutEvent()


class WindowCloseAttemptedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return WindowCloseAttemptedEvent()
