import abc
from enum import Enum
from typing import List, Optional

from cart_player.backend.api.dtos import CartInfo, GameData, GameImage, GameMetadata
from cart_player.frontend.domain.events import Event


class AppStatus(str, Enum):
    NOT_RUNNING = "not_running"
    UPDATING_CART_INFO = "updating_cart_info"
    UPDATING_PROGRESS_BAR = "updating_progress_bar"
    WAITING_FOR_EVENT = "waiting_for_events"


class App(abc.ABC):
    """Interface for an app."""

    @property
    @abc.abstractmethod
    def status(self) -> AppStatus:
        """App status."""
        pass

    @property
    @abc.abstractmethod
    def last_game_image(self) -> GameImage:
        """Last game image received by the app during a cart data update."""
        pass

    @abc.abstractmethod
    def start(self):
        """Start the app."""
        pass

    @abc.abstractmethod
    def wait_for_event(self) -> Event:
        """Wait until an event occurs and returns it."""
        pass

    @abc.abstractmethod
    def reset_progress_bar(self):
        """Reset progress bar to 0."""
        pass

    @abc.abstractmethod
    def update_progress_bar(self, *args, **kwargs):
        """Update progress bar if (i) it's active and (ii) the provided value is higher than the current count.

        Raises:
            RuntimeError: Try to update before a reset() or after a complete().
        """
        pass

    @abc.abstractmethod
    def update_eta(self, *args, **kwargs):
        """Update eta if (i) progress bar is active.

        Raises:
            RuntimeError: Try to update before a reset() or after a complete() of progress bar.
        """
        pass

    @abc.abstractmethod
    def complete_progress_bar(self, failure: bool):
        """Set progress bar status to complete.

        Args:
            failure: True if the task has failed, False otherwise.
        """
        pass

    @abc.abstractmethod
    def updating_cart_data(self, max_delay: float = 1.0):
        """
        Notifies app cart data will be updated soon.

        Args:
            max_delay: Max delay in seconds waiting for app to be in expected status before raising an exception.
        """
        pass

    @abc.abstractmethod
    def update_cart_data(
        self,
        cart_info: Optional[CartInfo],
        game_data_list: Optional[List[GameData]],
        game_metadata: Optional[GameMetadata],
        game_image: Optional[GameImage],
    ):
        """Update cart data.

        Args:
            cart_info: Cart info (ignored if None).
            game_data_list: List of game data (ignored if None).
            game_metadata: Game metadata (ignored if None).
            game_image: Game image (ignored if None).
        """
        pass

    @abc.abstractmethod
    def start_game_session(self):
        """Start a game session."""
        pass

    @abc.abstractmethod
    def end_game_session(self):
        """End a game session."""
        pass

    @abc.abstractmethod
    def freeze(self):
        """Freeze app, preventing user to trigger any event."""
        pass

    @abc.abstractmethod
    def unfreeze(self):
        """Unfreeze app, allowing user to trigger events."""
        pass

    @abc.abstractmethod
    def open_play_window(self):
        """Open a pop-up window for playing the inserted game."""
        pass

    @abc.abstractmethod
    def open_data_window(self):
        """Open a pop-up window for managing data game."""
        pass

    @abc.abstractmethod
    def open_settings_window(self):
        """Open a pop-up window for managing app settings."""
        pass

    @abc.abstractmethod
    def open_pop_up_warning_window(self, message: str):
        """Open a pop-up window for displaying a warning message."""
        pass

    @abc.abstractmethod
    def open_pop_up_error_window(self, message: str, close_app: bool):
        """Open a pop-up window for displaying an error."""
        pass

    @abc.abstractmethod
    def restore_previous_window(self):
        """Restore previous window."""
        pass
