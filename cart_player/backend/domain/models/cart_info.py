from __future__ import annotations

import pickle
import re
from typing import Optional

from cart_player.backend.domain.dtos import CartInfo as CartInfoDTO
from cart_player.backend.utils.models import GameRegion, GameSupport

from .cart_info_base_name_excluded import EXCLUDED_CHUNKS, SPECIAL_REGEX_PATTERN

LOADABLE_ATTRIBUTES = ["id_override", "image_ratio_override"]


class CartInfo:
    """Gathers information about a cart.

    Args:
        title: Cart title.
        header_checksum: Cart header checksum.
        support: Game support.
        region: Game region.
        id_override: Override for the identifier of a cart.
        image_ratio_override: Override for the image ratio.
        save_supported: True if cart support saving, False otherwise.

    Attributes:
        title: Cart title.
        code: Cart code.
        header_checksum: Cart header checksum.
        support: Game support.
        region: Game region.
        id_override: Override for the identifier of a cart.
        image_ratio_override: Override for the image ratio.
        save_supported: True if cart support saving, False otherwise.
        sgb_supported: True if cart support SGB mode, False otherwise.

    Properties:
        id: Identifier of a cart.
        image_ratio: Image ratio.
    """

    def __init__(
        self,
        title: str,
        code: str,
        header_checksum: str,
        support: GameSupport,
        region: GameRegion = GameRegion.UNKNOWN,
        id_override: Optional[str] = None,
        image_ratio_override: Optional[float] = None,
        save_supported: bool = False,
        sgb_supported: bool = False,
    ):
        self.title = title
        self.code = code
        self.header_checksum = header_checksum
        self.support = support
        self.region = region
        self.id_override = id_override
        self.image_ratio_override = image_ratio_override
        self.save_supported = save_supported
        self.sgb_supported = sgb_supported

    @property
    def id(self) -> str:
        """Cart identifier."""
        return CartInfoDTO._build_id(self.title, self.code, self.header_checksum, self.id_override)

    @property
    def image_ratio(self) -> float:
        """Image ratio."""
        return CartInfoDTO._build_image_ratio(self.region, self.support, self.image_ratio_override)

    @property
    def base_name(self) -> str:
        """Base name of the game."""
        base_name = self.id.strip()
        for chunk in sorted(EXCLUDED_CHUNKS, reverse=True):
            base_name = base_name.replace(rf"{chunk}", "").strip().replace("  ", " ")

        base_name = re.sub(SPECIAL_REGEX_PATTERN, "", base_name).strip()

        return base_name

    @property
    def cart_filename(self) -> str:
        """Name of the cart file."""
        return f"{self.title}_{self.code}@{self.header_checksum}.{self.cart_file_extension}"

    @property
    def cart_file_extension(self) -> str:
        """Extension of the cart file. It does not include the leading period."""
        return "json"

    @property
    def game_filename(self) -> str:
        """Name of the game file."""
        return f"{self.id}.{self.game_file_extension}"

    @property
    def game_file_extension(self) -> str:
        """Extension of the game file. It does not include the leading period."""
        return {
            GameSupport.GAMEBOY: "gb",
            GameSupport.GAMEBOY_COLOR: "gbc",
            GameSupport.GAMEBOY_OR_GAMEBOY_COLOR: "gbc",
            GameSupport.GAMEBOY_ADVANCE: "gba",
        }[self.support]

    @property
    def base_save_filename(self) -> str:
        """Base name of the save file (not historized)"""
        return f"{self.id}.{self.save_file_extension}"

    @property
    def save_file_extension(self) -> str:
        """Extension of the save file. It does not include the leading period."""
        return "sav"

    @property
    def metadata_filename(self) -> str:
        """Name of the metadata file."""
        return f"{self.id}.{self.metadata_file_extension}"

    @property
    def metadata_file_extension(self) -> str:
        """Extension of the metadata file. It does not include the leading period."""
        return "json"

    @property
    def image_filename(self) -> str:
        """Name of the image file."""
        return f"{self.id}.{self.image_file_extension}"

    @property
    def image_file_extension(self) -> str:
        """Extension of the image file. It does not include the leading period."""
        return "png"

    @property
    def pocket_image_file_extension(self) -> str:
        """Extension of the pocket image file. It does not include the leading period."""
        return "bin"

    def bytes(self) -> bytes:
        return pickle.dumps({k: v for k, v in self.__dict__.items() if k in LOADABLE_ATTRIBUTES})

    def __str__(self):
        return (
            f"CartInfo({self.title=}, {self.code=}, {self.header_checksum=}, {self.support=}, {self.region=}, "
            f"{self.id_override=}, {self.image_ratio_override=}, "
            f"{self.id=}, {self.image_ratio})"
        )

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.__dict__ == other.__dict__
        return False

    def load_from_bytes(self, data: bytes):
        """Load provided data into a CartInfo model. This operation does not affect excluded attributes."""
        cart_info_dict = {k: v for k, v in pickle.loads(data).items() if k in LOADABLE_ATTRIBUTES}
        for k, v in cart_info_dict.items():
            try:
                setattr(self, k, v)
            except AttributeError:
                continue

    @staticmethod
    def create(dto: CartInfoDTO):
        """Create a CartInfo model from the provided DTO."""
        return CartInfo(
            title=dto.title,
            code=dto.code,
            header_checksum=dto.header_checksum,
            support=dto.support,
            region=dto.region,
            id_override=dto.id_override,
            image_ratio_override=dto.image_ratio_override,
            save_supported=dto.save_supported,
            sgb_supported=dto.sgb_supported,
        )
