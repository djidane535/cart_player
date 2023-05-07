from cart_player.backend.adapters.game_library.utils import LaunchboxMetadataParser
from cart_player.backend.domain.models import CartInfo, GameMetadata
from cart_player.backend.domain.ports import GameMetadataLibrary
from cart_player.backend.utils.models import GameSupport

BASE_PATH = "./cart_player/backend/resources/launchbox"


class LaunchboxMetadataLibrary(GameMetadataLibrary):
    def __init__(self):
        self.parser = LaunchboxMetadataParser()

    def get_metadata(self, cart_info: CartInfo) -> GameMetadata:
        game_metadata = GameMetadata()

        # Browse all metadat fields
        support_filename = self._get_support_filename(cart_info.support)

        # Load text
        filepath = f"{BASE_PATH}/{support_filename}"
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        # Parse text and merge extracted game metadata with current one
        game_metadata.add_from(self.parser.parse_text(text, cart_info))

        return game_metadata

    def _get_support_filename(cls, support: GameSupport) -> str:
        return {
            GameSupport.GAMEBOY: "Nintendo - Game Boy.json",
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: "Nintendo - Game Boy Color.json",
            GameSupport.GAMEBOY_COLOR: "Nintendo - Game Boy Color.json",
            GameSupport.GAMEBOY_ADVANCE: "Nintendo - Game Boy Advance.json",
        }[support]
