from pathlib import Path
from typing import List

import FreeSimpleGUI as sg

from cart_player.backend.utils.models import GBXFlasherMode

from ..app_context import AppContext
from .component_builders import ComponentKey, FolderBrowseBuilder, FrameBuilder, InBuilder


class SettingsLayoutBuilder:
    """Builder for settings layout."""

    # >> Structure <<
    # +--------+
    # + MEMORY +
    # +--------+
    #
    @staticmethod
    def build(context: AppContext) -> List[sg.Element]:
        """Return the organized list of components"""
        return [SettingsLayoutBuilder._build_memory_components(context.memory_path, context.flasher_preferred_mode)]

    # >> MEMORY structure <<
    # +-----------------------------+
    # + <IN> | MEMORY_FOLDER_BROWSE +
    # +-----------------------------+
    #
    @staticmethod
    def _build_memory_components(memory_path: Path, flasher_preferred_mode: GBXFlasherMode) -> List[sg.Element]:
        """Return the organized list of memory components."""
        return [
            [
                FrameBuilder.build(
                    "Memory",
                    [
                        [
                            InBuilder.build(
                                default=str(memory_path),
                                key=ComponentKey.INPUT_MEMORY_FOLDER,
                            ),
                            FolderBrowseBuilder.build(
                                initial_folder=str(memory_path),
                                target=ComponentKey.INPUT_MEMORY_FOLDER,
                                key=ComponentKey.FOLDER_BROWSE_MEMORY_FOLDER,
                            ),
                        ],
                    ],
                ).set_expand_x()
            ],
            [
                FrameBuilder.build(
                    "GBX flasher preferred mode",
                    [
                        [
                            sg.Combo(
                                [v.prettify() for v in list(GBXFlasherMode)],
                                default_value=flasher_preferred_mode.prettify(),
                                expand_x=True,
                                size=(40, 0),
                                key=ComponentKey.GBX_FLASHER_PREFERRED_MODE_COMBO,
                                enable_events=True,
                            ),
                        ],
                    ],
                ).set_expand_x()
            ],
        ]
