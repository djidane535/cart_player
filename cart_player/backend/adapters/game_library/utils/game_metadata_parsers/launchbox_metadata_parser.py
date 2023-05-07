import json
import re
from typing import Dict, Optional

from rapidfuzz import fuzz
from unidecode import unidecode

from cart_player.backend.domain.models import CartInfo, GameMetadata

from .game_metadata_parser import GameMetadataParser

DESCR_KEY = "descr"
RELEASE_KEY = "release"


class LaunchboxMetadataParser(GameMetadataParser):
    def _parse_text(self, text: str, cart_info: CartInfo) -> GameMetadata:
        name = LaunchboxMetadataParser._preprocess_string(cart_info.base_name)
        db: Dict[str, Dict[str, Optional[str]]] = json.loads(text)
        entries = [(LaunchboxMetadataParser._preprocess_string(entry[0]), entry[1]) for entry in db.items()]
        entries.sort(key=lambda entry: LaunchboxMetadataParser._ratio(name, entry[0]), reverse=True)

        entry_data = entries[0] if LaunchboxMetadataParser._ratio(name, entries[0][0]) > 0.8 else None
        if not entry_data:
            return GameMetadata()

        return GameMetadata(description=entry_data[1][DESCR_KEY] or None, release=entry_data[1][RELEASE_KEY] or None)

    @staticmethod
    def _preprocess_string(s):
        s = unidecode(s.lower())
        s = re.sub(r'[^a-z0-9 ]', '', s)
        return s

    @staticmethod
    def _ratio(seq1: str, seq2: str) -> float:
        return fuzz.token_set_ratio(seq1, seq2) / 100
