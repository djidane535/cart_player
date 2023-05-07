import base64
import functools
import logging
import os
import sys
import time
from datetime import timedelta
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import PySimpleGUI as sg

from cart_player.backend.api.dtos import CartInfo, GameData, GameImage, GameMetadata, LocalMemoryConfiguration
from cart_player.backend.api.models import GameDataType
from cart_player.core.utils import lockedclass, lockedmethod
from cart_player.frontend import config
from cart_player.frontend.domain.commands import StopAppCommand
from cart_player.frontend.domain.events import (
    BackupButtonPressedEvent,
    DataSelectorButtonPressedEvent,
    EndSessionButtonPressedEvent,
    EraseButtonPressedEvent,
    Event,
    InputMemoryFolderButtonPressedEvent,
    InstallButtonPressedEvent,
    LaunchButtonPressedEvent,
    OpenMemoryButtonPressedEvent,
    PlaySelectorButtonPressedEvent,
    PopUpWindowIsClosingEvent,
    RefreshButtonPressedEvent,
    SettingsSelectorButtonPressedEvent,
    UploadButtonPressedEvent,
    WindowCloseAttemptedEvent,
    WindowReadNoWindowEvent,
    WindowReadTimeoutEvent,
)
from cart_player.frontend.domain.ports import App, AppStatus, LocalMemoryConfigurable
from cart_player.frontend.resources import app_icon_fullsize_filepath

from cart_player.settings import BASE_APP_PATH
from .utils import (
    DATA_WINDOW_TITLE,
    GAME_IMAGE_SQUARE_SIZE,
    MAIN_WINDOW_TITLE,
    PLAY_WINDOW_TITLE,
    POP_UP_MESSAGE_WIDTH,
    SETTINGS_WINDOW_TITLE,
    VALUE_TEXT_MAX_LINES_PER_KEY,
    VALUE_TEXT_WIDTH,
    AppContext,
    ComponentKey,
    DataLayoutBuilder,
    Focusable,
    Freezable,
    MainLayoutBuilder,
    PlayLayoutBuilder,
    PopUpErrorWindowLayoutBuilder,
    PopUpWarningWindowLayoutBuilder,
    PopUpWindowSelectorBuilder,
    SettingsLayoutBuilder,
    WindowType,
    build_existing_saves,
    put_image_into_square,
    wrap_text,
)

NO_WINDOW_EVENT = "-NO_WINDOW_EVENT-"
logger = logging.getLogger(f"{config.LOGGER_NAME}::SgApp")


@lockedclass
class SgApp(App, LocalMemoryConfigurable):
    """Cart player app."""

    def __init__(self, app_name: str, memory_path: Union[Path, str]):
        if os.name == 'posix':  # for macOS and Linux
            self._mac_os_fix()

        sg.theme("DarkGrey5")
        self._status = AppStatus.NOT_RUNNING
        self._icon = base64.b64encode(open(app_icon_fullsize_filepath, "rb").read())
        self._windows = []
        self._progress_bar = None
        self._eta = None
        self._last_game_image: GameImage = GameImage()

        # Data used to build context
        # Must only be updated through SgApp::_update_context() method
        #
        self._ctx_in_game_session: bool = False
        self._ctx_cart_info: Optional[CartInfo] = None
        self._ctx_cart_id: Optional[str] = None
        self._ctx_cart_save_supported: bool = False
        self._ctx_cart_sgb_supported: bool = False
        self._ctx_is_game_installed: bool = False
        self._ctx_game_name: Optional[str] = None
        self._ctx_game_saves_list: List[str] = []
        self._ctx_memory_path = Path(memory_path or self._request_memory_path(app_name))

    @property
    def status(self) -> AppStatus:
        return self._status

    @property
    def last_game_image(self) -> Optional[GameImage]:
        return self._last_game_image

    @property
    def memory_path(self) -> str:
        context = self._build_context()
        return context.memory_path

    def _mac_os_fix(self):
        # see:
        #   * https://github.com/PySimpleGUI/PySimpleGUI/issues/5471#issuecomment-1362602139
        #   * https://github.com/PySimpleGUI/PySimpleGUI/issues/5471#issuecomment-1155669914

        # This prevents an issue on macOS when using night mode where disabled input fields are rendered with black text
        # on a black background.
        uInput = functools.partial(
            sg.Input, disabled_readonly_background_color='white', disabled_readonly_text_color='black'
        )
        sg.Input = uInput

        # This prevents an issue on macOS where the window is rendered transparent.
        uWindow = functools.partial(
            sg.Window,
            alpha_channel=0.99,
        )
        sg.Window = uWindow

        logger.info("Mac OS fix applied!")

    def _request_memory_path(self, app_name: str) -> str:
        default_path = BASE_APP_PATH
        if os.name == 'nt':  # for Windows
            default_path = default_path.parent
        initial_folder = default_path
        initial_folder.mkdir(parents=True, exist_ok=True)
        memory_parent_path = sg.popup_get_folder(
            "Please select location for the new folder 'memory'",
            title="Select memory location",
            default_path=str(default_path),
            initial_folder=(str(initial_folder)),
        )
        if memory_parent_path is None:
            sys.exit()

        return str(Path(memory_parent_path) / "memory")

    def update_local_memory_config(self, local_memory_config: LocalMemoryConfiguration):
        self._ctx_memory_path = local_memory_config.root_path

    @lockedmethod
    def start(self):
        import base64

        # Configure main window
        context = self._build_context()
        pop_up_window_selector = PopUpWindowSelectorBuilder.build()
        main_layout = MainLayoutBuilder.build(context)
        layout = [pop_up_window_selector, [sg.HorizontalSeparator()], [main_layout]]
        self._close_app = False
        self._windows = []
        self._windows.append(
            sg.Window(
                MAIN_WINDOW_TITLE,
                layout,
                use_default_focus=False,
                enable_close_attempted_event=True,
                finalize=True,
                icon=self._icon,
            ),
        )
        self._progress_bar = self._get_component(ComponentKey.DATA_WINDOW_PROGRESS_BAR)
        self._eta = self._get_component(ComponentKey.DATA_WINDOW_ETA)
        self._disable_focus_on_top_window()

        self._status = AppStatus.WAITING_FOR_EVENT

    def wait_for_event(self) -> Event:
        # Check if app must be stopped
        if self._close_app:
            return StopAppCommand()

        # Event reading
        name, values = self._windows[-1].read() if self._windows else (NO_WINDOW_EVENT, None)

        logger.debug(f"wait_for_event(): {name=}, {values=}")

        # Build event and return it
        context = self._build_context()
        f = self._convert_to_event_build_function(name, context)
        kwargs = self._convert_to_event_build_function_kwargs(values, f, context)
        return f(**kwargs)

    def _build_context(self) -> AppContext:
        """Build the context of the app."""
        current_window = WindowType.from_str(self._windows[-1].Title if len(self._windows) > 0 else None)
        new_save_name = f"{self._ctx_cart_id}.sav" if self._ctx_cart_id else None
        status = self._status
        pending_task = status in [
            AppStatus.UPDATING_CART_INFO,
            AppStatus.UPDATING_PROGRESS_BAR,
        ]

        return AppContext(
            in_game_session=self._ctx_in_game_session,
            cart_info=self._ctx_cart_info,
            cart_id=self._ctx_cart_id,
            cart_save_supported=self._ctx_cart_save_supported,
            cart_sgb_supported=self._ctx_cart_sgb_supported,
            is_game_installed=self._ctx_is_game_installed,
            game_name=self._ctx_game_name,
            game_saves_list=self._ctx_game_saves_list,
            new_save_name=new_save_name,
            current_window=current_window,
            is_running=status != AppStatus.NOT_RUNNING,
            in_pop_up_window=len(self._windows) > 1,
            pending_task=pending_task,
            memory_path=self._ctx_memory_path,
        )

    def reset_progress_bar(self):
        if not self._progress_bar:
            raise ValueError("There is no progress bar.")

        if self.status != AppStatus.WAITING_FOR_EVENT:
            raise RuntimeError(
                f"Cannot reset progress bar when 'status={str(self.status)}'.",
            )

        self._status = AppStatus.UPDATING_PROGRESS_BAR
        self._progress_bar.reset()

    def update_progress_bar(self, current_count: int):
        if not self._progress_bar:
            raise ValueError("There is no progress bar.")

        if self.status != AppStatus.UPDATING_PROGRESS_BAR:
            raise RuntimeError(
                f"Cannot update progress bar when 'status={str(self.status)}'.",
            )

        self._progress_bar.update(current_count=current_count)

    def update_eta(self, eta: timedelta):
        if not self._eta:
            raise ValueError("There is no ETA text.")

        if self.status != AppStatus.UPDATING_PROGRESS_BAR:
            raise RuntimeError(
                f"Cannot update ETA when 'status={str(self.status)}'.",
            )

        if eta:
            hours = int(eta.total_seconds() // 3600)
            minutes = int((eta.total_seconds() % 3600) // 60)
            seconds = int(eta.total_seconds() % 60)
            eta_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            self._eta.update(f"ETA: {eta_str}")
        else:
            self._eta.update("ETA: 00:00:00")

    def complete_progress_bar(self, failure: bool):
        if not self._progress_bar:
            raise ValueError("There is no progress bar.")

        if self.status != AppStatus.UPDATING_PROGRESS_BAR:
            raise RuntimeError(
                f"Cannot complete progress bar when 'status={str(self.status)}'.",
            )

        self._progress_bar.complete(failure)
        self._status = AppStatus.WAITING_FOR_EVENT

    def updating_cart_data(self, max_delay: float = 1.0):
        current_delay = 0.0
        while current_delay < max_delay and self._status != AppStatus.WAITING_FOR_EVENT:
            time.sleep(0.1)
            current_delay += 0.1

        if self._status != AppStatus.WAITING_FOR_EVENT:
            raise RuntimeError(
                f"Cannot wait for cart data when 'status={str(self.status)}'.",
            )

        self._status = AppStatus.UPDATING_CART_INFO
        self._freeze()

    def update_cart_data(
        self,
        cart_info: Optional[CartInfo],
        game_data_list: Optional[List[GameData]],
        game_metadata: Optional[GameMetadata],
        game_image: Optional[GameImage],
    ):
        if self._status != AppStatus.UPDATING_CART_INFO:
            raise RuntimeError(
                f"Cannot update from cart info when 'status={str(self.status)}'.",
            )

        self._update_context(cart_info, game_data_list)

        context = self._build_context()
        if context.current_window == MAIN_WINDOW_TITLE:
            self._update_main_window_components(cart_info, game_metadata, game_image)
            self._unfreeze()
        if context.current_window == PLAY_WINDOW_TITLE:
            self._update_play_window_components(context)
        if context.current_window == DATA_WINDOW_TITLE:
            self._update_data_window_components(context)

        self._status = AppStatus.WAITING_FOR_EVENT

    def start_game_session(self):
        self._ctx_in_game_session = True
        context = self._build_context()
        self._update_play_window_components(context)

    def end_game_session(self):
        self._ctx_in_game_session = False
        context = self._build_context()
        self._update_play_window_components(context)

    def _update_context(self, cart_info: CartInfo, game_data_list: List[GameData]):
        self._ctx_cart_info = cart_info
        self._ctx_cart_id = cart_info.id
        self._ctx_cart_save_supported = cart_info.save_supported
        self._ctx_cart_sgb_supported = cart_info.sgb_supported

        if game_data_list is None:
            self._ctx_is_game_installed = False
            self._ctx_game_name = None
            self._ctx_game_saves_list = None
        else:
            game_file = next((game_data for game_data in game_data_list if game_data.type == GameDataType.GAME), None)
            self._ctx_game_name = game_file.name if game_file else None
            self._ctx_is_game_installed = game_file is not None

            game_data_list.sort(key=lambda game_data: game_data.date, reverse=True)
            self._ctx_game_saves_list = [
                game_data for game_data in game_data_list if game_data.type == GameDataType.SAVE
            ]

    def _update_main_window_components(
        self,
        cart_info: Optional[CartInfo],
        game_metadata: Optional[GameMetadata],
        game_image: Optional[GameImage],
    ):
        if game_metadata is not None:
            self._update_game_metadata(game_metadata)
        if game_image is not None:
            self._update_game_image(cart_info, game_image)

    def _update_game_metadata(self, game_metadata: GameMetadata):
        # Update info displayed
        for attr, value_key in [
            ("name", ComponentKey.GAME_CART_BOX_VALUE_NAME),
            ("description", ComponentKey.GAME_CART_BOX_VALUE_DESCRIPTION),
            ("platform", ComponentKey.GAME_CART_BOX_VALUE_PLATFORM),
            ("genre", ComponentKey.GAME_CART_BOX_VALUE_GENRE),
            ("developer", ComponentKey.GAME_CART_BOX_VALUE_DEVELOPER),
            ("region", ComponentKey.GAME_CART_BOX_VALUE_REGION),
            ("release", ComponentKey.GAME_CART_BOX_VALUE_RELEASE),
        ]:
            value_text = self._get_component(value_key)
            text = getattr(game_metadata, attr)
            if text is not None:
                text = getattr(game_metadata, attr)
            else:
                text = MainLayoutBuilder.default_game_cart_box_info_value_text()

            text = wrap_text(
                text,
                VALUE_TEXT_WIDTH,
                VALUE_TEXT_MAX_LINES_PER_KEY[value_key],
            )
            if value_text:
                value_text.update(text)

    def _update_game_image(self, cart_info: Optional[CartInfo], game_image: GameImage):
        # Update image displayed
        image_box = self._get_component(ComponentKey.GAME_CART_BOX_IMAGE)
        if game_image.data:
            squared_image_data = put_image_into_square(
                game_image.data,
                GAME_IMAGE_SQUARE_SIZE,
                cart_info.image_ratio,
            )
            image_box.update(data=squared_image_data)
            self._last_game_image = GameImage(data=squared_image_data)
        else:
            image_box.update(
                filename=MainLayoutBuilder.default_game_cart_box_image_filepath(),
            )
            self._last_game_image = GameImage()

    def _update_play_window_components(self, context: AppContext):
        # Launch button
        self._update_freeze_status(context, self._get_component(ComponentKey.LAUNCH_BUTTON))
        self._update_freeze_status(context, self._get_component(ComponentKey.END_SESSION))

    def _update_data_window_components(self, context: AppContext):
        # Memory
        self._update_freeze_status(context, self._get_component(ComponentKey.OPEN_MEMORY_FOLDER))

        # Install game box
        component = self._get_component(ComponentKey.INSTALL_GAME_BOX_GAME_NAME)
        component.update(value=DataLayoutBuilder.build_game_name(context))
        self._update_freeze_status(context, self._get_component(ComponentKey.INSTALL_BUTTON))

        # Download save box
        component = self._get_component(ComponentKey.DOWNLOAD_SAVE_BOX_SAVE_NAME)
        component.update(value=DataLayoutBuilder.build_new_save_name(context))
        self._update_freeze_status(context, self._get_component(ComponentKey.BACKUP_BUTTON))

        # Upload save box
        component = self._get_component(ComponentKey.UPLOAD_SAVE_BOX_SAVE_NAMES_COMBO)
        existing_saves_list = build_existing_saves(context)
        component.update(values=existing_saves_list, value=existing_saves_list[0])
        self._update_freeze_status(context, self._get_component(ComponentKey.UPLOAD_BUTTON))

        # Erase save box
        self._update_freeze_status(context, self._get_component(ComponentKey.ERASE_BUTTON))

    @lockedmethod
    def freeze(self):
        self._freeze()

    def _freeze(self):
        """Freeze app, allowing user to trigger events.
        Perform the actual operation on the elements of the current window.
        """
        if self.status == AppStatus.NOT_RUNNING:
            raise RuntimeError(f"Cannot freeze app when 'status={str(self.status)}'.")

        for key in ComponentKey:
            element = self._get_component(key)
            if isinstance(element, Freezable):
                element.freeze()

    @lockedmethod
    def unfreeze(self):
        self._unfreeze()

    def _unfreeze(self):
        """Unfreeze app, allowing user to trigger events.
        Perform the actual operation on the elements of the current window.
        """
        if self.status == AppStatus.NOT_RUNNING:
            raise RuntimeError(f"Cannot unfreeze app when 'status={str(self.status)}'.")

        for key in ComponentKey:
            element = self._get_component(key)
            if isinstance(element, Freezable):
                element.unfreeze()

    def _update_freeze_status(self, context: AppContext, component):
        if not component:
            return

        is_frozen = False
        if component.key == ComponentKey.OPEN_MEMORY_FOLDER:
            is_frozen = not DataLayoutBuilder.can_enable_open_memory_folder_button(context)
        if component.key == ComponentKey.INSTALL_BUTTON:
            is_frozen = not DataLayoutBuilder.can_enable_install_button(context)
        if component.key == ComponentKey.BACKUP_BUTTON:
            is_frozen = not DataLayoutBuilder.can_enable_download_button(context)
        if component.key == ComponentKey.UPLOAD_BUTTON:
            is_frozen = not DataLayoutBuilder.can_enable_upload_button(context)
        if component.key == ComponentKey.LAUNCH_BUTTON:
            is_frozen = not PlayLayoutBuilder.can_enable_launch_button(context)
        if component.key == ComponentKey.END_SESSION:
            is_frozen = not PlayLayoutBuilder.can_enable_end_session_button(context)

        if is_frozen:
            component.freeze()
        else:
            component.unfreeze()

    def _can_unfreeze(self, context: AppContext, element: ComponentKey):
        return isinstance(element, Freezable) and not self._can_freeze(context, element)

    @lockedmethod
    def open_play_window(self):
        """Open a pop-up window for playing the inserted game."""
        if self.status != AppStatus.WAITING_FOR_EVENT:
            raise RuntimeError(
                f"Cannot open play window when 'status={str(self.status)}'.",
            )

        self._freeze()

        context = self._build_context()
        play_layout = PlayLayoutBuilder.build(context)
        self._windows.append(
            sg.Window(
                PLAY_WINDOW_TITLE,
                play_layout,
                modal=True,
                enable_close_attempted_event=True,
                finalize=True,
                icon=self._icon,
            ),
        )
        self._progress_bar = None
        self._disable_focus_on_top_window()

    @lockedmethod
    def open_data_window(self):
        """Open a pop-up window for managing data game."""
        if self.status != AppStatus.WAITING_FOR_EVENT:
            raise RuntimeError(
                f"Cannot open data window when 'status={str(self.status)}'.",
            )

        self._freeze()

        context = self._build_context()
        data_layout = DataLayoutBuilder.build(context)
        self._windows.append(
            sg.Window(
                DATA_WINDOW_TITLE,
                data_layout,
                modal=True,
                enable_close_attempted_event=True,
                finalize=True,
                icon=self._icon,
            ),
        )
        self._progress_bar = self._get_component(ComponentKey.DATA_WINDOW_PROGRESS_BAR)
        self._eta = self._get_component(ComponentKey.DATA_WINDOW_ETA)
        self._disable_focus_on_top_window()

    @lockedmethod
    def open_settings_window(self):
        """Open a pop-up window for managing app settings."""
        if self.status != AppStatus.WAITING_FOR_EVENT:
            raise RuntimeError(
                f"Cannot open data window when 'status={str(self.status)}'.",
            )

        self._freeze()

        context = self._build_context()
        settings_layout = SettingsLayoutBuilder.build(context)
        self._windows.append(
            sg.Window(
                SETTINGS_WINDOW_TITLE,
                settings_layout,
                modal=True,
                enable_close_attempted_event=True,
                finalize=True,
                icon=self._icon,
            ),
        )
        self._progress_bar = None
        self._disable_focus_on_top_window()

    def open_pop_up_warning_window(self, message: str):
        """Open a pop-up window for displaying an error."""
        close_button_name = "Close"
        popup_window = sg.Window(
            "WARNING",
            layout=PopUpWarningWindowLayoutBuilder.build(
                wrap_text(message, POP_UP_MESSAGE_WIDTH, 100, True),
                close_button_name,
                icon=self._icon,
            ),
            modal=True,
            keep_on_top=True,
        )
        while True:
            event, _ = popup_window.read()
            if event == close_button_name or event == sg.WIN_CLOSED:
                break
        popup_window.close()

    def open_pop_up_error_window(self, message: str, close_app: bool):
        """Open a pop-up window for displaying an error."""
        close_button_name = "Close"
        popup_window = sg.Window(
            "ERROR",
            layout=PopUpErrorWindowLayoutBuilder.build(
                wrap_text(message, POP_UP_MESSAGE_WIDTH, 100, True),
                close_button_name,
                icon=self._icon,
            ),
            modal=True,
            keep_on_top=True,
        )
        while True:
            event, _ = popup_window.read()
            if event == close_button_name or event == sg.WIN_CLOSED:
                break
        popup_window.close()
        self._close_app = close_app

    @lockedmethod
    def restore_previous_window(
        self,
    ):
        """Restore the previous window."""
        if self.status != AppStatus.WAITING_FOR_EVENT:
            raise RuntimeError(
                f"Cannot restore previous window when 'status={str(self.status)}'.",
            )

        n_windows = len(self._windows)
        if n_windows <= 1:
            raise ValueError(f"No window left to restore ({n_windows=}).")

        self._windows[-1].close()
        self._windows.pop()
        self._progress_bar = (
            self._get_component(ComponentKey.DATA_WINDOW_PROGRESS_BAR)
            if self._build_context().current_window == WindowType.DATA
            else None
        )
        self._progress_bar = (
            self._get_component(ComponentKey.DATA_WINDOW_ETA)
            if self._build_context().current_window == WindowType.DATA
            else None
        )

        # Drop messages received meanwhile on previous window
        while True:
            name, _ = self._windows[-1].read(0)
            if name in [sg.TIMEOUT_EVENT, sg.WIN_CLOSED, None]:
                break

        self._unfreeze()

    @lockedmethod
    def stop(self):
        """Stop application."""
        if self._status == AppStatus.NOT_RUNNING:
            logger.info("App is already stopped.", exc_info=True)

        self._status = AppStatus.NOT_RUNNING
        while len(self._windows) > 0:
            self._windows[-1].close()
            self._windows = self._windows[:-1]

    @classmethod
    def _convert_to_event_build_function(
        cls,
        key: str,
        context: AppContext,
    ) -> Callable:
        """Convert provided key to an event build function based on app context."""
        # Handle events depending on context
        if not context.is_running or context.pending_task:
            return WindowReadNoWindowEvent.create

        if key == sg.WIN_CLOSE_ATTEMPTED_EVENT and context.in_pop_up_window:
            return PopUpWindowIsClosingEvent.create

        if key == sg.WIN_CLOSE_ATTEMPTED_EVENT and not context.in_pop_up_window:
            return WindowCloseAttemptedEvent.create

        # Handle events not depending on context
        constructor_mapping = {
            # Pop-up window selector buttons
            ComponentKey.PLAY_SELECTOR_BUTTON: PlaySelectorButtonPressedEvent.create,
            ComponentKey.DATA_SELECTOR_BUTTON: DataSelectorButtonPressedEvent.create,
            ComponentKey.SETTINGS_SELECTOR_BUTTON: SettingsSelectorButtonPressedEvent.create,
            # Buttons
            ComponentKey.BACKUP_BUTTON: BackupButtonPressedEvent.create,
            ComponentKey.INPUT_MEMORY_FOLDER: InputMemoryFolderButtonPressedEvent.create,
            ComponentKey.INSTALL_BUTTON: InstallButtonPressedEvent.create,
            ComponentKey.LAUNCH_BUTTON: LaunchButtonPressedEvent.create,
            ComponentKey.END_SESSION: EndSessionButtonPressedEvent.create,
            ComponentKey.REFRESH_BUTTON: RefreshButtonPressedEvent.create,
            ComponentKey.UPLOAD_BUTTON: UploadButtonPressedEvent.create,
            ComponentKey.ERASE_BUTTON: EraseButtonPressedEvent.create,
            ComponentKey.OPEN_MEMORY_FOLDER: OpenMemoryButtonPressedEvent.create,
            # Window
            sg.TIMEOUT_EVENT: WindowReadTimeoutEvent.create,  # not used anymore
            # TODO emit BackupSaveFileAfterPlayingCommand when app is closing (just in case)
        }
        return constructor_mapping.get(key, WindowReadNoWindowEvent.create)

    def _disable_focus_on_top_window(self):
        """Disable focus on top window."""
        for key in ComponentKey:
            element = self._get_component(key)
            if isinstance(element, Focusable) and element.Widget is not None:
                element.Widget.config(takefocus=0)

    def _get_component(self, key: str) -> Optional[sg.Element]:
        """Return sg.Element with the given key if it exists, None otherwise."""
        element = self._windows[-1].find_element(key, True) if len(self._windows) > 0 else None
        return element if not isinstance(element, sg.ErrorElement) else None

    @classmethod
    def _convert_to_event_build_function_kwargs(
        cls,
        values: Any,
        event_build_function: Callable,
        context: AppContext,
    ):
        """Converted provided values to kwargs expected by the provided event build function."""
        if event_build_function == LaunchButtonPressedEvent.create:
            game_save = SgApp._get_game_save(context, values, ComponentKey.PLAY_SAVE_BOX_SAVE_NAMES_COMBO)
            return {
                "game_name": context.game_name,
                "save_name": game_save.name if game_save else None,
                "game_session_path": context.memory_path / Path("session"),
            }
        if event_build_function == InputMemoryFolderButtonPressedEvent.create:
            return {"path_str": values.get(ComponentKey.INPUT_MEMORY_FOLDER, None)}
        if event_build_function in [PopUpWindowIsClosingEvent.create, EndSessionButtonPressedEvent.create]:
            return {
                "play_window_is_closing": context.current_window == WindowType.PLAY,
                "cart_info": context.cart_info,
                "game_session_path": context.memory_path / Path("session"),
            }
        if event_build_function == UploadButtonPressedEvent.create:
            game_save = SgApp._get_game_save(context, values, ComponentKey.UPLOAD_SAVE_BOX_SAVE_NAMES_COMBO)
            return {"save_name": game_save.name if game_save else None}
        if event_build_function == OpenMemoryButtonPressedEvent.create:
            return {"memory_path": context.memory_path}

        return {}

    @classmethod
    def _get_game_save(cls, context: AppContext, values: Dict[str, str], key: str):
        try:
            combo_str = values.get(key, None)
            save_rank = int(combo_str.split(".")[0]) if combo_str and len(combo_str.split(".")) > 0 else None
            return context.game_saves_list[save_rank - 1] if save_rank is not None else None
        except ValueError:  # no save to load
            return None
