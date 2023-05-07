from typing import Optional

from pydantic import BaseModel

from cart_player.backend.utils.models import GameRegion, GameSupport


class CartInfo(BaseModel):
    title: Optional[str]
    header_checksum: Optional[str]
    code: Optional[str]
    support: Optional[GameSupport]
    region: Optional[GameRegion] = GameRegion.UNKNOWN
    id_override: Optional[str] = None
    image_ratio_override: Optional[float] = None
    save_supported: bool = False
    sgb_supported: bool = False

    @property
    def id(self) -> Optional[str]:
        if self.title or self.code or self.header_checksum or self.id_override:
            return CartInfo._build_id(self.title, self.code, self.header_checksum, self.id_override)
        return None

    @property
    def image_ratio(self) -> float:
        return CartInfo._build_image_ratio(self.region, self.support, self.image_ratio_override)

    @staticmethod
    def _build_id(title: str, code: str, header_checksum: str, id_override: Optional[str]) -> float:
        """Build the cart identifier."""
        return id_override if id_override is not None else f"{title}_{code}${header_checksum}"

    @staticmethod
    def _build_image_ratio(region: GameRegion, support: GameSupport, image_ratio_override: Optional[float]) -> float:
        """Build the image ratio (width / height)."""
        if image_ratio_override is not None and image_ratio_override > 0:
            return image_ratio_override
        if region == GameRegion.UNKNOWN:
            return None
        if GameRegion.is_europe_or_usa(region):
            return 1
        # JAPAN - GAMEBOY | GAMEBOY_COLOR
        if GameSupport.is_gameboy_or_gameboy_color(support):
            # TODO rough estimate (different for GB / GBC?)
            #      see https://retroprotection.com/Japanese-Game-Boy-Color-Box-Protectors-10-pack-823.htm
            #
            return 10.0 / 12.4
        # JAPAN - GAMEBOY ADVANCE
        return 1.6  # TODO rough estimate from pictures
