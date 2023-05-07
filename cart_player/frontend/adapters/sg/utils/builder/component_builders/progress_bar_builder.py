from typing import Any, Dict, Tuple

import PySimpleGUI as sg

from cart_player.core.utils import lockedclass, lockedmethod

from .component_key import ComponentKey


class ProgressBarBuilder:
    @staticmethod
    def build(key: ComponentKey) -> sg.Button:
        """Build a progress bar."""
        return ProgressBar(
            max_value=100,
            size=(10, 10),
            orientation="h",
            expand_x=True,
            bar_color=("#f5a52c", sg.theme_progress_bar_color()[1]),
            key=key,
        )


@lockedclass
class ProgressBar(sg.ProgressBar):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._current_count = 0
        self._active = False

    @property
    def current_count(self) -> int:
        """Current progress bar count."""
        return self._current_count

    @lockedmethod
    def reset(self):
        """Reset progress bar to 0."""
        super().update(current_count=0)
        self._active = True
        self._current_count = 0

    @lockedmethod
    def update(self, *args, **kwargs):
        """
        Update progress bar if (i) it's active and (ii) the provided value is higher than the current count.

        Raises:
            RuntimeError: Try to update before a reset() or after a complete().
        """
        if not self._active:
            raise RuntimeError("Cannot update an inactive ProgressBar.")

        current_count = self._get_current_count_from_args_kwargs(*args, **kwargs)
        if current_count is None or current_count < self.current_count:
            args, kwargs = self._remove_current_count_from_args_kwargs(*args, **kwargs)
            return super().update(*args, **kwargs)

        super().update(*args, **kwargs)
        self._current_count = current_count

    @lockedmethod
    def complete(self, failure: bool):
        """Set progress bar status to complete.

        Args:
            failure: True if the task has failed, False otherwise.
        """
        new_count = 100 if not failure else 0
        super().update(current_count=new_count)
        self._active = False
        self._current_count = new_count

    def _get_current_count_from_args_kwargs(self, *args, **kwargs):
        """Extract argument 'current_count' from *args or **kwargs if it exists, return None otherwise."""
        if len(args) > 0:
            return args[0]
        if kwargs.get("current_count"):
            return kwargs["current_count"]
        return None

    def _remove_current_count_from_args_kwargs(
        self,
        *args,
        **kwargs,
    ) -> Tuple[Tuple, Dict[str, Any]]:
        """Remove argument 'current_count' from *args or **kwargs if it exists."""
        args_list = list(args)
        n_kwargs = dict(kwargs)
        if len(args) > 0:
            args_list[0] = None
        if kwargs.get("current_count"):
            n_kwargs["current_count"] = None

        n_args = tuple(args_list)
        return n_args, n_kwargs
