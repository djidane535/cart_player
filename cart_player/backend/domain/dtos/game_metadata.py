from typing import Optional

from pydantic import BaseModel


class GameMetadata(BaseModel):
    name: Optional[str]
    description: Optional[str]
    platform: Optional[str]
    genre: Optional[str]
    developer: Optional[str]
    region: Optional[str]
    release: Optional[str]
    crc: Optional[str]
