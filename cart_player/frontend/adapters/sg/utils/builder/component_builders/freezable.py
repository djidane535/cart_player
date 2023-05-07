import abc


class Freezable(abc.ABC):
    @abc.abstractmethod
    def freeze(self):
        """Freeze component, preventing user to trigger any event."""
        pass

    @abc.abstractmethod
    def unfreeze(self):
        """Unfreeze component, allowing user to trigger events."""
        pass
