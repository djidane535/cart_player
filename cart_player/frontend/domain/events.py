from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from cart_player.backend.api.dtos import CartInfo
from cart_player.core.domain.messages import BaseMessage
from cart_player.frontend import config

logger = logging.getLogger(f"{config.LOGGER_NAME}::Event")


class Event(BaseMessage):
    pass


class BackupButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return BackupButtonPressedEvent()


class DataSelectorButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return DataSelectorButtonPressedEvent()


class EraseButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return EraseButtonPressedEvent()


class InputMemoryFolderButtonPressedEvent(BaseMessage):
    path_str: str

    @staticmethod
    def create(path_str: str) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return InputMemoryFolderButtonPressedEvent(path_str=path_str)


class InstallButtonPressedEvent(BaseMessage):
    @staticmethod
    def create() -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return InstallButtonPressedEvent()


class LaunchButtonPressedEvent(BaseMessage):
    game_name: str
    save_name: Optional[str] = None
    game_session_path: Path = None

    @staticmethod
    def create(game_name: str, save_name: str, game_session_path: Path) -> Event:
        """Create an event based on event values returned by an sg.Window."""
        return LaunchButtonPressedEvent(game_name=game_name, save_name=save_name, game_session_path=game_session_path)


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
