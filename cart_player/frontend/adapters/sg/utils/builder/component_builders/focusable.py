import abc


class Focusable(abc.ABC):
    @abc.abstractmethod
    def disable_focus(self):
        """Disable focus on component, preventing user to set focus in this component."""
        pass

    @abc.abstractmethod
    def enable_focus(self):
        """Enable focus on component, allowing user to set focus in this component."""
        pass
