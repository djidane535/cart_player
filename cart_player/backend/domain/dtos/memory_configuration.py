from pathlib import Path

from pydantic import BaseModel


class MemoryConfiguration(BaseModel):
    pass


class LocalMemoryConfiguration(MemoryConfiguration):
    root_path: Path
