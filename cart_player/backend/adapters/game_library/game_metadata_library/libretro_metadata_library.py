from collections import defaultdict

from cart_player.backend.adapters.game_library.utils import LibretroMetadatField, LibretroMetadatParser
from cart_player.backend.domain.models import CartInfo, GameMetadata
from cart_player.backend.domain.ports import GameMetadataLibrary
from cart_player.backend.utils.models import GameSupport

BASE_PATH = "./cart_player/backend/resources/libretro/libretro-database/metadat"
LIBRETRO_METADAT_MAP = defaultdict()
LIBRETRO_METADAT_MAP.update(
    {
        LibretroMetadatField.GENRE: f"{BASE_PATH}/genre",
        LibretroMetadatField.DEVELOPER: f"{BASE_PATH}/developer",
        LibretroMetadatField.RELEASEYEAR: f"{BASE_PATH}/releaseyear",
        LibretroMetadatField.CRC: f"{BASE_PATH}/developer",
    }
)


class LibretroMetadataLibrary(GameMetadataLibrary):
    def __init__(self):
        self.parsers = {field: LibretroMetadatParser(field) for field in LibretroMetadatField}

    def get_metadata(self, cart_info: CartInfo) -> GameMetadata:
        game_metadata = GameMetadata()

        # Browse all metadat fields
        support_filename = self._get_support_filename(cart_info.support)
        for field in LibretroMetadatField:
            # Load text
            base_filepath = LIBRETRO_METADAT_MAP[field]
            filepath = f"{base_filepath}/{support_filename}"
            with open(filepath, "r") as f:
                text = f.read()

            # Parse text and merge extracted game metadata with current one
            parser = self.parsers[field]
            game_metadata.add_from(parser.parse_text(text, cart_info))

        return game_metadata

    def _get_support_filename(cls, support: GameSupport) -> str:
        return {
            GameSupport.GAMEBOY: "Nintendo - Game Boy.dat",
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: "Nintendo - Game Boy Color.dat",
            GameSupport.GAMEBOY_COLOR: "Nintendo - Game Boy Color.dat",
            GameSupport.GAMEBOY_ADVANCE: "Nintendo - Game Boy Advance.dat",
        }[support]
