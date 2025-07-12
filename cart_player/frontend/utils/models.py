from __future__ import annotations

from enum import Enum


class EditWindowType(str, Enum):
    """Edit window type."""

    GAME_BOX_IMAGE = "GAME_BOX_IMAGE"
    GAME_NAME = "NAME"
    GAME_DESCRIPTION = "DESCRIPTION"
    GAME_PLATFORM = "PLATFORM"
    GAME_GENRE = "GENRE"
    GAME_DEVELOPER = "DEVELOPER"
    GAME_REGION = "REGION"
    GAME_RELEASE = "RELEASE"
    GAME_CRC = "CRC"
