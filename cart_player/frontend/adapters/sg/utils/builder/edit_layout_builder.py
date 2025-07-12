from pathlib import Path
from typing import List

import FreeSimpleGUI as sg

from cart_player.frontend.utils.models import EditWindowType

from ..app_context import AppContext
from .component_builders import (
    ButtonBuilder,
    ComponentKey,
    FileBrowseBuilder,
    FrameBuilder,
    InBuilder,
    MultilineBuilder,
    TextBuilder,
)

EDIT_WINDOW_TITLE = "EDIT"

class EditLayoutBuilder:
    """Builder for edit layout."""

    # >> Structure <<
    #
    # EDIT_GAME_BOX_IMAGE
    # +------------------------+
    # + <PATH> <BROWSE>        +
    # + <APPLY>                +
    # +------------------------+
    #
    # EDIT_XXX
    # +------------------------+
    # + <INPUT_TEXT>           +
    # + <APPLY>                +
    # +------------------------+
    #
    @classmethod
    def build(cls, context: AppContext, type: EditWindowType) -> List[sg.Element]:
        """Return the organized list of components"""
        apply_button_key = cls._get_apply_key(type)
        edit_components = cls._get_edit_components(type, context)        

        return [
            edit_components,
            [
                [
                    sg.Push(),
                    ButtonBuilder.build(
                        "APPLY",
                        "Apply changes.",
                        key=apply_button_key,
                    ),
                    sg.Push(),
                ],
            ],
        ]
    
    @staticmethod
    def _get_apply_key(type: EditWindowType) -> str:
        return {
            EditWindowType.GAME_BOX_IMAGE: ComponentKey.EDIT_GAME_BOX_IMAGE_APPLY_BUTTON,
            EditWindowType.GAME_NAME: ComponentKey.EDIT_GAME_NAME_APPLY_BUTTON,
            EditWindowType.GAME_DESCRIPTION: ComponentKey.EDIT_GAME_DESCRIPTION_APPLY_BUTTON,
            EditWindowType.GAME_PLATFORM: ComponentKey.EDIT_GAME_PLATFORM_APPLY_BUTTON,
            EditWindowType.GAME_GENRE: ComponentKey.EDIT_GAME_GENRE_APPLY_BUTTON,
            EditWindowType.GAME_DEVELOPER: ComponentKey.EDIT_GAME_DEVELOPER_APPLY_BUTTON,
            EditWindowType.GAME_REGION: ComponentKey.EDIT_GAME_REGION_APPLY_BUTTON,
            EditWindowType.GAME_RELEASE: ComponentKey.EDIT_GAME_RELEASE_APPLY_BUTTON,
            EditWindowType.GAME_CRC: ComponentKey.EDIT_GAME_CRC_APPLY_BUTTON,
        }[type]
    
    @classmethod
    def _get_edit_components(cls, type: EditWindowType, context: AppContext) -> List:
        if type == EditWindowType.GAME_BOX_IMAGE:
            return cls._build_input_image_components(type)
        elif type == EditWindowType.GAME_DESCRIPTION:
            return cls._build_multiline_components(type, context)
        return cls._build_input_text_components(type, context)
    

    @classmethod
    def _build_input_image_components(cls, type: EditWindowType) -> List:
        return [
            FrameBuilder.build(
                cls._get_frame_title(type),
                [
                    [
                        InBuilder.build(
                            default="",
                            key=ComponentKey.INPUT_GAME_BOX_IMAGE_FILE,
                        ),
                        FileBrowseBuilder.build(
                            initial_folder=str(Path.home()),
                            target=ComponentKey.INPUT_GAME_BOX_IMAGE_FILE,
                            key=ComponentKey.FOLDER_BROWSE_GAME_BOX_IMAGE_FILE,
                            file_types=[("Image file (png)", "*.png"), ("Image file (jpg)", "*.jpg")],
                        ),
                    ],
                ],
            ),
        ]

    @classmethod
    def _build_input_text_components(cls, type: EditWindowType, context: AppContext) -> List:
        title = cls._get_frame_title(type)
        content = cls._get_current_content(type, context)
        text_input_key = {
            EditWindowType.GAME_NAME: ComponentKey.INPUT_GAME_NAME,
            EditWindowType.GAME_PLATFORM: ComponentKey.INPUT_GAME_PLATFORM,
            EditWindowType.GAME_GENRE: ComponentKey.INPUT_GAME_GENRE,
            EditWindowType.GAME_DEVELOPER: ComponentKey.INPUT_GAME_DEVELOPER,
            EditWindowType.GAME_REGION: ComponentKey.INPUT_GAME_REGION,
            EditWindowType.GAME_RELEASE: ComponentKey.INPUT_GAME_RELEASE,
            EditWindowType.GAME_CRC: ComponentKey.INPUT_GAME_CRC,
        }[type]
        return [FrameBuilder.build(title, [[TextBuilder.build(content=content, editable=True, key=text_input_key)]])]

    @classmethod
    def _build_multiline_components(cls, type: EditWindowType, context: AppContext) -> List:
        title = cls._get_frame_title(type)
        content = cls._get_current_content(type, context)
        multiline_key = {
            EditWindowType.GAME_DESCRIPTION: ComponentKey.INPUT_GAME_DESCRIPTION
        }[type]
        return [
            FrameBuilder.build(
                title,
                [[MultilineBuilder.build(content=content, editable=True, size=(60, 15), key=multiline_key)]]
            ),
        ]

    @staticmethod
    def _get_frame_title(type: EditWindowType) -> str:
        return {
            EditWindowType.GAME_BOX_IMAGE: "Game box image",
            EditWindowType.GAME_NAME: "Name",
            EditWindowType.GAME_DESCRIPTION: "Description",
            EditWindowType.GAME_PLATFORM: "Platform",
            EditWindowType.GAME_GENRE: "Genre",
            EditWindowType.GAME_DEVELOPER: "Developer",
            EditWindowType.GAME_REGION: "Region",
            EditWindowType.GAME_RELEASE: "Release",
            EditWindowType.GAME_CRC: "CRC",
        }[type]
    
    @staticmethod
    def _get_current_content(type: EditWindowType, context: AppContext) -> str:
        if not context.game_metadata:
            return ""
        elif type == EditWindowType.GAME_NAME:
            return context.game_metadata.name or ""
        elif type == EditWindowType.GAME_DESCRIPTION:
            return context.game_metadata.description or ""
        elif type == EditWindowType.GAME_PLATFORM:
            return context.game_metadata.platform or ""
        elif type == EditWindowType.GAME_GENRE:
            return context.game_metadata.genre or ""
        elif type == EditWindowType.GAME_DEVELOPER:
            return context.game_metadata.developer or ""
        elif type == EditWindowType.GAME_REGION:
            return context.game_metadata.region or ""
        elif type == EditWindowType.GAME_RELEASE:
            return context.game_metadata.release or ""
        elif type == EditWindowType.GAME_CRC:
            return context.game_metadata.crc or ""
    
        raise ValueError

    @staticmethod
    def _get_text_input_key(type: EditWindowType) -> str:
        return {
            EditWindowType.GAME_NAME: ComponentKey.INPUT_GAME_NAME,
            EditWindowType.GAME_DESCRIPTION: ComponentKey.INPUT_GAME_DESCRIPTION,
            EditWindowType.GAME_PLATFORM: ComponentKey.INPUT_GAME_PLATFORM,
            EditWindowType.GAME_GENRE: ComponentKey.INPUT_GAME_GENRE,
            EditWindowType.GAME_DEVELOPER: ComponentKey.INPUT_GAME_DEVELOPER,
            EditWindowType.GAME_REGION: ComponentKey.INPUT_GAME_REGION,
            EditWindowType.GAME_RELEASE: ComponentKey.INPUT_GAME_RELEASE,
            EditWindowType.GAME_CRC: ComponentKey.INPUT_GAME_CRC,
        }[type]