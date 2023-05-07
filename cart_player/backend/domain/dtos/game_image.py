from typing import Optional

from pydantic import BaseModel


class GameImage(BaseModel):
    data: Optional[bytes] = None
