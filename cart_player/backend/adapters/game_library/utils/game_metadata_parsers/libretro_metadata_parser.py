from collections import defaultdict
from enum import Enum

from cart_player.backend.domain.models import CartInfo, GameMetadata

from .game_metadata_parser import GameMetadataParser


class LibretroMetadatField(str, Enum):
    GENRE = "genre"
    DEVELOPER = "developer"
    RELEASEYEAR = "releaseyear"
    CRC = "crc"


class LibretroMetadatParser(GameMetadataParser):
    """Parser for extracting game metadata from Libretro metadata files."""

    def __init__(self, field: LibretroMetadatField):
        super().__init__()
        self.field = field

    def _parse_text(self, text: str, cart_info: CartInfo) -> GameMetadata:
        field_values = defaultdict(str)
        field_name = self.field.value
        try:
            field_values[field_name] = self._find(field_name, text, cart_info.id)
        except Exception:
            return GameMetadata()

        return GameMetadata(
            genre=field_values.get("genre", None),
            developer=field_values.get("developer", None),
            release=field_values.get("releaseyear", None),
            crc=field_values.get("crc", None),
        )

    @classmethod
    def _find(cls, field_name: str, text: str, cart_id: str) -> GameMetadata:
        """Find the value of a field in the given text, based on the given cart ID.

        Args:
            field_name: Name of the field to find.
            text: Text to search for the field.
            cart_id: ID of the game cartridge to search for.

        Returns:
            Value of the field.
        """
        # Split the content of the .dat file into lines
        lines = text.split("\n")

        # Iterate through the lines of the .dat file
        for i, line in enumerate(lines):
            if "comment" in line:
                comment = " ".join(line.split(" ")[1:]).strip('"')
                # Check if the comment matches the given cart_id
                if comment in cart_id or cart_id in comment:
                    # Find the next line with field_name
                    for j in range(i + 1, len(lines)):
                        if field_name in lines[j]:
                            # Extract and return the value after field_name
                            return " ".join(lines[j].split(" ")[1:]).strip('"')

        # Return None if the cart_id was not found
        return None
