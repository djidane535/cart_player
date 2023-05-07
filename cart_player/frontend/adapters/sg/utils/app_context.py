from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseModel

from cart_player.backend.api.dtos import CartInfo, GameData

MAIN_WINDOW_TITLE = "Cart Player"
PLAY_WINDOW_TITLE = "PLAY"
DATA_WINDOW_TITLE = "DATA"
UNKNOWN_WINDOW = "UNKNOWN"
SETTINGS_WINDOW_TITLE = "SETTINGS"


class WindowType(str, Enum):
    MAIN = MAIN_WINDOW_TITLE
    PLAY = PLAY_WINDOW_TITLE
    DATA = DATA_WINDOW_TITLE
    SETTINGS = SETTINGS_WINDOW_TITLE
    UNKNOWN = UNKNOWN_WINDOW

    @staticmethod
    def from_str(s):
        if s == WindowType.MAIN:
            return WindowType.MAIN
        if s == WindowType.PLAY:
            return WindowType.PLAY
        if s == WindowType.DATA:
            return WindowType.DATA
        if s == WindowType.SETTINGS:
            return WindowType.SETTINGS
        else:
            return WindowType.UNKNOWN


class AppContext(BaseModel):
    # Game metadata
    in_game_session: bool
    cart_info: Optional[CartInfo]
    cart_id: Optional[str]
    cart_save_supported: bool
    cart_sgb_supported: bool
    is_game_installed: bool
    game_name: Optional[str]
    game_saves_list: List[GameData]
    new_save_name: Optional[str]

    # Window
    current_window: WindowType

    # Status
    is_running: bool
    in_pop_up_window: bool
    pending_task: bool

    # Settings
    memory_path: Path

    @property
    def cart_inserted(self) -> bool:
        return self.cart_id is not None
