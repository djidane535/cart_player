from pathlib import Path
from typing import List

import PySimpleGUI as sg

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
        return [SettingsLayoutBuilder._build_memory_components(context.memory_path)]

    # >> MEMORY structure <<
    # +-----------------------------+
    # + <IN> | MEMORY_FOLDER_BROWSE +
    # +-----------------------------+
    #
    @staticmethod
    def _build_memory_components(memory_path: Path) -> List[sg.Element]:
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
        ]
