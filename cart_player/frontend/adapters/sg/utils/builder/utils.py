from typing import List

from ..app_context import AppContext

DEFAULT_NO_SAVE_IN_COMBO = "-- NO SAVE --"


def build_existing_saves(context: AppContext) -> List[str]:
    if not context.game_saves_list or not context.cart_inserted:
        return [DEFAULT_NO_SAVE_IN_COMBO]

    existing_saves = []
    for i, game_data in enumerate(context.game_saves_list, start=1):
        existing_save = f"{i}. {game_data.date.strftime('%Y-%m-%d %H:%M:%S')}"
        if game_data.metadata:
            origin = game_data.metadata.get("tag", None)
            existing_save += f" [{origin}]" if origin else ""
        existing_saves.append(existing_save)
    return existing_saves
