from pydantic import BaseModel

from cart_player.backend.utils.models import GBXFlasherMode


class CartFlasherConfiguration(BaseModel):
    pass


class GBXFlasherConfiguration(CartFlasherConfiguration):
    preferred_mode: GBXFlasherMode
