from pathlib import Path
from typing import List

import PySimpleGUI as sg

from ..app_context import AppContext
from .component_builders import ButtonBuilder, ComponentKey, FrameBuilder, ProgressBarBuilder, TextBuilder
from .utils import build_existing_saves


class DataLayoutBuilder:
    """Builder for data layout."""

    # >> Structure <<
    # +--------+
    # + BODY   +
    # + FOOTER +
    # +--------+
    #
    @staticmethod
    def build(context: AppContext) -> List[sg.Element]:
        """Return the organized list of components"""
        memory_path = DataLayoutBuilder.build_memory_path(context)
        game_name = DataLayoutBuilder.build_game_name(context)
        new_save_name = DataLayoutBuilder.build_new_save_name(context)
        existing_saves = build_existing_saves(context)
        enable_open_memory_folder_button = DataLayoutBuilder.can_enable_open_memory_folder_button(context)
        enable_install_button = DataLayoutBuilder.can_enable_install_button(context)
        enable_download_button = DataLayoutBuilder.can_enable_download_button(context)
        enable_upload_button = DataLayoutBuilder.can_enable_upload_button(context)
        enable_erase_button = DataLayoutBuilder.can_enable_erase_button(context)

        return [
            DataLayoutBuilder._build_body_components(
                memory_path,
                game_name,
                existing_saves,
                new_save_name,
                enable_open_memory_folder_button,
                enable_install_button,
                enable_download_button,
                enable_upload_button,
                enable_erase_button,
            ),
            DataLayoutBuilder._build_footer_components(),
        ]

    @staticmethod
    def build_memory_path(context: AppContext) -> str:
        return context.memory_path

    @staticmethod
    def build_game_name(context: AppContext) -> str:
        return context.game_name or "NOT INSTALLED"

    @staticmethod
    def build_new_save_name(context: AppContext) -> str:
        if not DataLayoutBuilder.can_enable_download_button(context):
            return "UNSUPPORTED"
        return context.new_save_name

    @staticmethod
    def can_enable_open_memory_folder_button(context: AppContext) -> bool:
        return context.memory_path.exists()

    @staticmethod
    def can_enable_install_button(context: AppContext) -> bool:
        return not context.is_game_installed and context.cart_inserted

    @staticmethod
    def can_enable_download_button(context: AppContext) -> bool:
        return context.cart_save_supported and context.cart_inserted

    @staticmethod
    def can_enable_upload_button(context: AppContext) -> bool:
        return DataLayoutBuilder.can_enable_download_button(context) and len(context.game_saves_list) > 0

    @staticmethod
    def can_enable_erase_button(context: AppContext) -> bool:
        return context.cart_save_supported and context.cart_inserted

    # +-------------------+
    # + MEMORY            +
    # + INSTALL_GAME_BOX  +
    # + DOWNLOAD_SAVE_BOX +
    # + UPLOAD_SAVE_BOX   +
    # + ERASE_SAVE_BOX    +
    # +-------------------+
    @staticmethod
    def _build_body_components(
        memory_path: Path,
        game_name: str,
        existing_saves: List[str],
        new_save_name: str,
        enable_open_memory_folder_button: bool = True,
        enable_install_button: bool = True,
        enable_download_button: bool = True,
        enable_upload_button: bool = True,
        enable_erase_button: bool = True,
    ) -> List[sg.Element]:
        """Return the organized list of body components."""
        return [
            DataLayoutBuilder._build_memory_components(memory_path, enable_open_memory_folder_button),
            DataLayoutBuilder._build_install_game_box_components(
                game_name,
                enable_install_button,
            ),
            DataLayoutBuilder._build_download_save_box_components(
                new_save_name,
                enable_download_button,
            ),
            DataLayoutBuilder._build_upload_save_box_components(
                existing_saves,
                enable_upload_button,
            ),
            DataLayoutBuilder._build_erase_save_box_components(
                enable_erase_button,
            ),
        ]

    @staticmethod
    def _build_memory_components(memory_path: Path, enable_open_memory_folder_button: bool) -> List[sg.Element]:
        """Return the organized list of memory components."""
        return [
            FrameBuilder.build(
                "Memory",
                [
                    [TextBuilder.build("Open the memory directory.")],
                    [
                        sg.Push(),
                        ButtonBuilder.build(
                            "OPEN",
                            "Open the memory directory.",
                            disabled=not enable_open_memory_folder_button,
                            key=ComponentKey.OPEN_MEMORY_FOLDER,
                        ),
                    ],
                ],
            ).set_expand_x(),
        ]

    @staticmethod
    def _build_install_game_box_components(
        game_name: str,
        enable_button: bool = True,
    ) -> List[sg.Element]:
        """Return the organized list of install game box components."""
        return [
            FrameBuilder.build(
                "Install game",
                [
                    [TextBuilder.build("Store game data from cartrige into memory.")],
                    [
                        sg.Push(),
                        TextBuilder.build(
                            game_name,
                            key=ComponentKey.INSTALL_GAME_BOX_GAME_NAME,
                        ),
                        sg.Push(),
                        ButtonBuilder.build(
                            "INSTALL",
                            "Install your game (required for playing).",
                            disabled=not enable_button,
                            key=ComponentKey.INSTALL_BUTTON,
                        ),
                    ],
                ],
            ).set_expand_x(),
        ]

    @staticmethod
    def _build_download_save_box_components(
        new_save_name: str,
        enable_button: bool = True,
    ) -> List[sg.Element]:
        """Return the organized list of download save box components."""
        return [
            FrameBuilder.build(
                "Download save",
                [
                    [TextBuilder.build("Store save data from cartrige into memory.")],
                    [
                        sg.Push(),
                        TextBuilder.build(
                            new_save_name,
                            key=ComponentKey.DOWNLOAD_SAVE_BOX_SAVE_NAME,
                        ),
                        sg.Push(),
                        ButtonBuilder.build(
                            "BACKUP",
                            "Backup the save of your cartridge.",
                            disabled=not enable_button,
                            key=ComponentKey.BACKUP_BUTTON,
                        ),
                    ],
                ],
            ).set_expand_x(),
        ]

    @staticmethod
    def _build_upload_save_box_components(
        existing_saves: List[str],
        enable_button: bool = True,
    ) -> List[sg.Element]:
        """Return the organized list of upload save box components."""
        return [
            FrameBuilder.build(
                "Upload save",
                [
                    [TextBuilder.build("Upload save data from memory into cartridge.")],
                    [
                        sg.Combo(
                            existing_saves,
                            default_value=existing_saves[0],
                            expand_x=True,
                            size=(40, 0),
                            key=ComponentKey.UPLOAD_SAVE_BOX_SAVE_NAMES_COMBO,
                        ),
                        ButtonBuilder.build(
                            "UPLOAD",
                            "Upload a save into your cartridge.",
                            disabled=not enable_button,
                            key=ComponentKey.UPLOAD_BUTTON,
                        ),
                    ],
                ],
            ).set_expand_x(),
        ]

    @staticmethod
    def _build_erase_save_box_components(enable_button: bool = True) -> List[sg.Element]:
        """Return the organized list of erase save box components."""
        return [
            FrameBuilder.build(
                "Erase save",
                [
                    [TextBuilder.build("Erase save data from cartridge.")],
                    [
                        sg.Push(),
                        ButtonBuilder.build(
                            "ERASE",
                            "Erase save from your cartridge.",
                            disabled=not enable_button,
                            key=ComponentKey.ERASE_BUTTON,
                            dangerous_button=True,
                        ),
                    ],
                ],
            ).set_expand_x(),
        ]

    # +--------------------------+
    # + DATA_WINDOW_PROGRESS_BAR +
    # +--------------------------+
    @staticmethod
    def _build_footer_components() -> List[sg.Element]:
        """Return the organized list of footer components."""
        return [
            ProgressBarBuilder.build(ComponentKey.DATA_WINDOW_PROGRESS_BAR),
            TextBuilder.build(content="ETA: 00:00:00", key=ComponentKey.DATA_WINDOW_ETA).set_font("bold"),
        ]
