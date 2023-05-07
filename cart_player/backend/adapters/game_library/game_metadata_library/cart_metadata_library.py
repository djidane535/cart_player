from typing import Optional

from cart_player.backend.domain.models import CartInfo, GameMetadata
from cart_player.backend.domain.ports import GameMetadataLibrary
from cart_player.backend.utils.models import GameRegion, GameSupport

PRETTY_SGB_SUPPORTED = "SGB compatible"


class CartMetadataLibrary(GameMetadataLibrary):
    def get_metadata(self, cart_info: CartInfo) -> GameMetadata:
        platform = self._prettify_support(cart_info.support)
        platform = f"{platform} ({PRETTY_SGB_SUPPORTED})" if platform and cart_info.sgb_supported else platform
        return GameMetadata(
            name=cart_info.base_name,
            platform=platform,
            region=self._prettify_region(cart_info.region),
        )

    @classmethod
    def _prettify_support(cls, support: GameSupport) -> Optional[str]:
        return {
            GameSupport.GAMEBOY: "GameBoy",
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: "GameBoy / GameBoy Color",
            GameSupport.GAMEBOY_COLOR: "GameBoy Color",
            GameSupport.GAMEBOY_ADVANCE: "GameBoy Advance",
        }[support]

    @classmethod
    def _prettify_region(cls, region: GameRegion) -> Optional[str]:
        return {
            GameRegion.WORLD: "World",
            GameRegion.EUROPE: "Europe",
            GameRegion.USA: "USA",
            GameRegion.AUSTRALIA: "Australia",
            GameRegion.JAPAN: "Japan",
            GameRegion.EUROPE_OR_USA: "Europe / USA",
            GameRegion.EUROPE_OR_AUSTRALIA: "Europe / Australia",
            GameRegion.UNKNOWN: "Unknown",
        }[region]
