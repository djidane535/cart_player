from __future__ import annotations

from enum import Enum


class GameRegion(str, Enum):
    """Game region."""

    WORLD = "WORLD"
    EUROPE = "EUROPE"
    USA = "USA"
    AUSTRALIA = "AUSTRALIA"
    JAPAN = "JAPAN"
    EUROPE_OR_USA = "EUROPE_OR_USA"
    EUROPE_OR_AUSTRALIA = "EUROPE_OR_AUSTRALIA"
    UNKNOWN = "UNKNOWN"

    @classmethod
    def is_europe_or_usa(cls, x: GameRegion) -> bool:
        return x in [cls.EUROPE, cls.USA, cls.EUROPE_OR_USA, cls.EUROPE_OR_AUSTRALIA, cls.WORLD]


class GameSupport(str, Enum):
    """Game support."""

    GAMEBOY = "GAMEBOY"
    GAMEBOY_OR_GAMEBOY_COLOR = "GAMEBOY_OR_GAMEBOY_COLOR"
    GAMEBOY_COLOR = "GAMEBOY_COLOR"
    GAMEBOY_ADVANCE = "GAMEBOY_ADVANCE"

    @classmethod
    def is_gameboy_or_gameboy_color(cls, x: GameSupport) -> bool:
        return x in [cls.GAMEBOY, cls.GAMEBOY_OR_GAMEBOY_COLOR, cls.GAMEBOY_COLOR]


class GameDataType(str, Enum):
    """Type of game data."""

    CART = "CART"
    GAME = "GAME"
    SAVE = "SAVE"
    METADATA = "METADATA"
    IMAGE = "IMAGE"
    ANALOGUE_POCKET_IMAGE = "ANALOGUE_POCKET_IMAGE"


class SaveDataOrigin(str, Enum):
    """Origin of save data."""

    CARTRIDGE = "CARTRIDGE"
    EMULATOR = "EMULATOR"
